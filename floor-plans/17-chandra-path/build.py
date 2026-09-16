import pymupdf, math, sys
from csedit import parse
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen

SRC="proposed.pdf"; OUT="Proposed_Floor_Plan-20260916-R1.pdf"
doc=pymupdf.open(SRC); page=doc[0]
D=page.derotation_matrix; M=page.rotation_matrix
GREY=(0.55294,0.55294,0.55294); FURN=(0.70196,0.70196,0.70196); PURPLE=(0.35294,0.28627,0.61176); BLACK=(0,0,0); BLUE=(0,0.49804,1)
FT=15.7  # pt per foot (displayed)

# ---------- 1. delete objects from content stream ----------
def disp_bbox(bb):
    x0,y0,x1,y1=bb
    pts=[(1684-y, 1191-x) for x,y in ((x0,y0),(x1,y1))]
    xs=[q[0] for q in pts]; ys=[q[1] for q in pts]
    return pymupdf.Rect(min(xs),min(ys),max(xs),max(ys))
DEL=[pymupdf.Rect(*r) for r in [
    (170.5,230.3,421.0,352.3),   # bedroom-01 interior (upper part incl. wardrobe hatch)
    (170.5,352.3,394.0,402.3),   # bedroom-01 interior lower part (keeps pillar-3 stub + its door)
    (170.5,411.2,330.5,501.0),   # old toilet interior + its door
    (170.5,501.0,340.0,663.5),   # bedroom-02 interior (label)
    (340.0,546.0,394.0,663.5),
    (394.0,511.5,561.0,664.2),   # kitchen interior + partition wall
    (437.0,492.5,484.7,512.0),   # old kitchen door jambs
    (439.0,496.0,482.5,539.0),   # old kitchen door arc
    (220.0,402.5,259.5,411.0),   # new utility door gap (clips partition face lines)
]]
DELEXACT=[pymupdf.Rect(150.5,402.8,345.4,410.7)]  # partition between kitchen and utility: redrawn with door gap
KEEP=[pymupdf.Rect(402.1,511.8,437.4,511.8)]  # wall face line
xrefs=page.get_contents()
data=b"".join(doc.xref_stream(x) for x in xrefs)
objs=parse(data)
def overlaps(r,z):
    return r.x0<=z.x1 and r.x1>=z.x0 and r.y0<=z.y1 and r.y1>=z.y0
def contained(r,z):
    return r.x0>=z.x0 and r.x1<=z.x1 and r.y0>=z.y0 and r.y1<=z.y1
def clip_seg(p0,p1,z):
    # returns list of sub-segments of p0-p1 lying OUTSIDE rect z (Liang-Barsky)
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]
    t0,t1=0.0,1.0
    for p,q in ((-dx,p0[0]-z.x0),(dx,z.x1-p0[0]),(-dy,p0[1]-z.y0),(dy,z.y1-p0[1])):
        if p==0:
            if q<0: return [(p0,p1)]
        else:
            t=q/p
            if p<0: t0=max(t0,t)
            else: t1=min(t1,t)
    if t0>=t1: return [(p0,p1)]
    res=[]
    if t0>0.001: res.append((p0,(p0[0]+dx*t0,p0[1]+dy*t0)))
    if t1<0.999: res.append(((p0[0]+dx*t1,p0[1]+dy*t1),p1))
    return res
BASE=(0.12,0.0,0.0,0.12,14.0,28.0)
def to_content(x,y):   # displayed -> content units under BASE ctm
    return ((1177-y)/0.12, (1656-x)/0.12)
edits=[]   # (start,end,replacement bytes)
ndel=nclip=0
for o in objs:
    r=disp_bbox(o[2])
    if any(abs(r.x0-k.x0)<0.3 and abs(r.y0-k.y0)<0.3 and abs(r.x1-k.x1)<0.3 and abs(r.y1-k.y1)<0.3 for k in KEEP): continue
    if any(contained(r,z) for z in DEL) or any(abs(r.x0-k.x0)<0.3 and abs(r.y0-k.y0)<0.3 and abs(r.x1-k.x1)<0.3 and abs(r.y1-k.y1)<0.3 for k in DELEXACT):
        edits.append((o[0],o[1],b"")); ndel+=1; continue
    if o[3]==b"S" and len(o[6])==2 and all(abs(a-b)<1e-6 for a,b in zip(o[5],BASE)) and any(overlaps(r,z) for z in DEL):
        # clip a straight outline line against the deletion zones
        pts=[(1684-y, 1191-x) for x,y in o[6]]   # displayed
        segs=[(pts[0],pts[1])]
        for z in DEL:
            nxt=[]
            for s0,s1 in segs: nxt+=clip_seg(s0,s1,z)
            segs=nxt
        if len(segs)==1 and segs[0]==(pts[0],pts[1]): continue
        rep=b""
        for s0,s1 in segs:
            a=to_content(*s0); b=to_content(*s1)
            rep+=b"%.1f %.1f m\n%.1f %.1f l\nS\n"%(a[0],a[1],b[0],b[1])
        edits.append((o[0],o[1],rep)); nclip+=1
print("deleting",ndel,"clipping",nclip,"of",len(objs))
out=bytearray(); pos=0
for a,b,rep in sorted(edits):
    out+=data[pos:a]; out+=rep; pos=b
out+=data[pos:]
doc.update_stream(xrefs[0],bytes(out))
for x in xrefs[1:]: doc.update_stream(x,b"\n")

# ---------- 2. drawing helpers (all coords in displayed/rotated space) ----------
sh=page.new_shape()
P=lambda x,y: pymupdf.Point(x,y)*D
def R(x0,y0,x1,y1):
    a=P(x0,y0); b=P(x1,y1); r=pymupdf.Rect(min(a.x,b.x),min(a.y,b.y),max(a.x,b.x),max(a.y,b.y)); return r
def wall(x0,y0,x1,y1):
    sh.draw_rect(R(x0,y0,x1,y1)); sh.finish(color=GREY,fill=GREY,width=0)
def line(x0,y0,x1,y1,color=BLACK,width=0,dashes=None):
    sh.draw_line(P(x0,y0),P(x1,y1)); sh.finish(color=color,width=width,dashes=dashes)
def rect(x0,y0,x1,y1,color=FURN,width=0.48,fill=None):
    sh.draw_rect(R(x0,y0,x1,y1)); sh.finish(color=color,width=width,fill=fill)
def circle(cx,cy,r,color=FURN,width=0.48):
    sh.draw_circle(P(cx,cy),r); sh.finish(color=color,width=width)
def arc(cx,cy,px,py,angle,color=BLACK,width=0):
    sh.draw_sector(P(cx,cy),P(px,py),angle,fullSector=False); sh.finish(color=color,width=width,closePath=False)
def rrect(x0,y0,x1,y1,r,color=FURN,width=0.48):
    # rounded rectangle via lines+arcs
    sh.draw_line(P(x0+r,y0),P(x1-r,y0)); sh.draw_sector(P(x1-r,y0+r),P(x1-r,y0),90,fullSector=False)
    sh.draw_line(P(x1,y0+r),P(x1,y1-r)); sh.draw_sector(P(x1-r,y1-r),P(x1,y1-r),90,fullSector=False)
    sh.draw_line(P(x1-r,y1),P(x0+r,y1)); sh.draw_sector(P(x0+r,y1-r),P(x0+r,y1),90,fullSector=False)
    sh.draw_line(P(x0,y1-r),P(x0,y0+r)); sh.draw_sector(P(x0+r,y0+r),P(x0,y0+r),90,fullSector=False)
    sh.finish(color=color,width=width,closePath=False)

def door(x0,y0,x1,y1,hinge,swing):
    """door in wall gap rect (x0,y0,x1,y1). hinge: 'x0'|'x1' (for horizontal wall) or 'y0'|'y1' (vertical wall).
    swing: 'up'|'down'|'left'|'right' = side of wall the leaf opens to."""
    horiz = (x1-x0) > (y1-y0)
    # wall end lines (black 0.96) + jamb rects (black 0.48, 3pt)
    if horiz:
        line(x0,y0,x0,y1,BLACK,0.96); line(x1,y0,x1,y1,BLACK,0.96)
        rect(x0,y0,x0+3,y1,BLACK,0.48); rect(x1-3,y0,x1,y1,BLACK,0.48)
        L=(x1-x0)-6
        hx = x0+3 if hinge=='x0' else x1-3
        dirn = -1 if swing=='up' else 1
        yw = y0 if swing=='up' else y1
        # leaf (1.3pt wide) perpendicular to wall
        lx0 = hx if hinge=='x0' else hx-1.3
        rect(lx0, min(yw,yw+dirn*L), lx0+1.3, max(yw,yw+dirn*L), BLACK,0)
        # arc from leaf tip to opposite jamb
        tip=(hx, yw+dirn*L); end=(x1-3 if hinge=='x0' else x0+3, yw)
        arc(hx,yw,tip[0],tip[1], 90 if (hinge=='x0')==(swing=='up') else -90)
        line(x0+3,yw,x1-3,yw,BLACK,0)  # threshold line
    else:
        line(x0,y0,x1,y0,BLACK,0.96); line(x0,y1,x1,y1,BLACK,0.96)
        rect(x0,y0,x1,y0+3,BLACK,0.48); rect(x0,y1-3,x1,y1,BLACK,0.48)
        L=(y1-y0)-6
        hy = y0+3 if hinge=='y0' else y1-3
        dirn = -1 if swing=='left' else 1
        xw = x0 if swing=='left' else x1
        ly0 = hy if hinge=='y0' else hy-1.3
        rect(min(xw,xw+dirn*L), ly0, max(xw,xw+dirn*L), ly0+1.3, BLACK,0)
        tip=(xw+dirn*L, hy)
        arc(xw,hy,tip[0],tip[1], 90 if (hinge=='y0')==(swing=='left') else -90)
        line(xw,y0+3,xw,y1-3,BLACK,0)

# text as outlines (Didact Gothic ~ Century Gothic)
font=TTFont("DidactGothicRegular.ttf"); gs=font.getGlyphSet(); cmap=font.getBestCmap(); upm=font["head"].unitsPerEm
def text(s, cx, y_base, size, align="center", color=BLACK):
    sc=size/upm
    adv=sum(font["hmtx"][cmap[ord(ch)]][0] for ch in s if ord(ch) in cmap)*sc
    x = cx-adv/2 if align=="center" else cx
    for ch in s:
        gname=cmap.get(ord(ch))
        if not gname: continue
        pen=DecomposingRecordingPen(gs); gs[gname].draw(pen)
        cur=None; start=None
        def tp(pt): return P(x+pt[0]*sc, y_base-pt[1]*sc)
        for op,args in pen.value:
            if op=="moveTo": cur=args[0]; start=cur
            elif op=="lineTo": sh.draw_line(tp(cur),tp(args[0])); cur=args[0]
            elif op=="qCurveTo":
                pts=list(args)
                if pts[-1] is None: pts[-1]=start
                # implied on-curve points
                ctrls=pts[:-1]; last=pts[-1]
                p0=cur
                for i,c in enumerate(ctrls):
                    p2 = last if i==len(ctrls)-1 else ((c[0]+ctrls[i+1][0])/2,(c[1]+ctrls[i+1][1])/2)
                    # flatten quadratic
                    prev=p0
                    for k in range(1,9):
                        t=k/8; q=((1-t)**2*p0[0]+2*(1-t)*t*c[0]+t*t*p2[0],(1-t)**2*p0[1]+2*(1-t)*t*c[1]+t*t*p2[1])
                        sh.draw_line(tp(prev),tp(q)); prev=q
                    p0=p2
                cur=last
            elif op=="curveTo":
                p0=cur; c1,c2,p3=args
                sh.draw_bezier(tp(p0),tp(c1),tp(c2),tp(p3)); cur=p3
            elif op in ("closePath","endPath"):
                if cur and start and cur!=start: sh.draw_line(tp(cur),tp(start))
                cur=None
        sh.finish(color=None,fill=color,width=0,even_odd=False,closePath=True)
        x+=font["hmtx"][gname][0]*sc

def label(name, dims, cx, cy):
    text(name, cx, cy, 8.0); 
    if dims: text(dims, cx, cy+9.5, 6.4)

# replay original drawings with a transform (for reusing fixture symbols)
orig=pymupdf.open(SRC)[0]
ODR=orig.get_drawings()
for it in ODR:
    r=pymupdf.Rect(it["rect"])*M; r.normalize(); it["drect"]=r
def replay(sel, mat):
    """sel: function(item)->bool on displayed rect; mat: pymupdf.Matrix applied in displayed space"""
    n=0
    T=M*mat*D   # unrotated -> displayed -> transform -> unrotated
    for it in ODR:
        if not sel(it): continue
        n+=1
        for itm in it["items"]:
            k=itm[0]
            if k=="l": sh.draw_line(itm[1]*T, itm[2]*T)
            elif k=="c": sh.draw_bezier(itm[1]*T, itm[2]*T, itm[3]*T, itm[4]*T)
            elif k=="re": sh.draw_polyline([q*T for q in itm[1].quad])  # rect -> quad
            elif k=="qu": sh.draw_polyline([itm[1].ul*T, itm[1].ur*T, itm[1].lr*T, itm[1].ll*T, itm[1].ul*T])
        sh.finish(color=it.get("color"), fill=it.get("fill"), width=it.get("width") or 0, dashes=it.get("dashes"),
                  closePath=it.get("closePath",False), even_odd=it.get("even_odd",False),
                  lineCap=max(it.get("lineCap") or (0,)) if it.get("lineCap") else 0, lineJoin=it.get("lineJoin") or 0)
    return n
def inside(z):
    z=pymupdf.Rect(z); return lambda it: z.contains(it["drect"])

exec(open("layout.py").read()) if not (len(sys.argv)>1 and sys.argv[1]=="delonly") else None

sh.commit(overlay=True)
doc.save(OUT, garbage=1, deflate=True)
print("saved",OUT)
