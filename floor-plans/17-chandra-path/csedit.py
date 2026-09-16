import re, pymupdf
TOK=re.compile(rb"/[^\s/\[\]<>(){}%]*|[-+]?\d*\.?\d+|\[|\]|<<|>>|\([^)]*\)|<[0-9A-Fa-f\s]*>|[A-Za-z'\"*]+|%[^\n]*")
NUM=re.compile(rb"^[-+]?\d*\.?\d+$")
PAINT={b"S",b"s",b"f",b"F",b"f*",b"B",b"B*",b"b",b"b*",b"n"}
CONS={b"m",b"l",b"c",b"v",b"y",b"re",b"h"}
def mul(a,b):
    return (a[0]*b[0]+a[1]*b[2], a[0]*b[1]+a[1]*b[3], a[2]*b[0]+a[3]*b[2], a[2]*b[1]+a[3]*b[3], a[4]*b[0]+a[5]*b[2]+b[4], a[4]*b[1]+a[5]*b[3]+b[5])
def apply(m,x,y): return (m[0]*x+m[2]*y+m[4], m[1]*x+m[3]*y+m[5])
def parse(data):
    """returns (path objects, text objects).
    path obj: (start,end,bbox_pdf,paint_op,linewidth,ctm,points)
    text obj: (start,end,pos_pdf) pos = first Tm/Td origin under CTM"""
    ctm=(1,0,0,1,0,0); stack=[]; operands=[]; objs=[]; texts=[]; lw=None
    cur=None; intext=False; opstart=None; tstart=None; tpos=None
    for m in TOK.finditer(data):
        t=m.group(0)
        if opstart is None: opstart=m.start()
        if NUM.match(t): operands.append(float(t)); continue
        if t[:1] in b"/[]<(%": operands.append(t); continue
        op=t
        if op==b"q": stack.append(ctm)
        elif op==b"Q": ctm=stack.pop() if stack else ctm
        elif op==b"cm" and len(operands)>=6: ctm=mul(tuple(operands[-6:]),ctm)
        elif op==b"w" and operands: lw=operands[-1]
        elif op==b"BT": intext=True; tstart=opstart; tpos=None
        elif op==b"ET":
            intext=False
            texts.append((tstart, m.end(), tpos))
        elif intext and op in (b"Tm",b"Td",b"TD") and tpos is None:
            nums=[v for v in operands if isinstance(v,float)]
            if op==b"Tm" and len(nums)>=6: tpos=apply(ctm,nums[-2],nums[-1])
            elif len(nums)>=2: tpos=apply(ctm,nums[-2],nums[-1])
        elif op in CONS and not intext:
            if cur is None: cur=[opstart,[]]
            nums=[v for v in operands if isinstance(v,float)]
            if op==b"re" and len(nums)>=4:
                x,y,w,h=nums[-4:]
                for px,py in ((x,y),(x+w,y),(x,y+h),(x+w,y+h)): cur[1].append(apply(ctm,px,py))
            elif op!=b"h":
                for i in range(0,len(nums)-1,2): cur[1].append(apply(ctm,nums[i],nums[i+1]))
        elif op in PAINT or op==b"W":
            if cur is not None and op in PAINT:
                pts=cur[1]
                if pts:
                    xs=[q[0] for q in pts]; ys=[q[1] for q in pts]
                    objs.append((cur[0], m.end(), (min(xs),min(ys),max(xs),max(ys)), op, lw, ctm, list(pts)))
                cur=None
        operands=[]; opstart=None
    return objs, texts

BASE=(0.12,0.0,0.0,0.12,14.0,28.0)
def disp_bbox(bb):
    x0,y0,x1,y1=bb
    pts=[(1684-y, 1191-x) for x,y in ((x0,y0),(x1,y1))]
    xs=[q[0] for q in pts]; ys=[q[1] for q in pts]
    return pymupdf.Rect(min(xs),min(ys),max(xs),max(ys))
def overlaps(r,z): return r.x0<=z.x1 and r.x1>=z.x0 and r.y0<=z.y1 and r.y1>=z.y0
def contained(r,z): return r.x0>=z.x0 and r.x1<=z.x1 and r.y0>=z.y0 and r.y1<=z.y1
def clip_seg(p0,p1,z):
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; t0,t1=0.0,1.0
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
def to_content(x,y): return ((1177-y)/0.12, (1656-x)/0.12)

def edit_page(doc, page, DEL, DELEXACT=(), KEEP=(), TEXTDEL=()):
    """delete path objects contained in DEL rects (displayed coords), clip straight lines crossing them,
    delete text objects whose origin lies in TEXTDEL rects."""
    xrefs=page.get_contents()
    data=b"".join(doc.xref_stream(x) for x in xrefs)
    objs,texts=parse(data)
    edits=[]; ndel=nclip=ntxt=0
    for o in objs:
        r=disp_bbox(o[2])
        if any(abs(r.x0-k.x0)<0.3 and abs(r.y0-k.y0)<0.3 and abs(r.x1-k.x1)<0.3 and abs(r.y1-k.y1)<0.3 for k in KEEP): continue
        if any(contained(r,z) for z in DEL) or any(abs(r.x0-k.x0)<0.3 and abs(r.y0-k.y0)<0.3 and abs(r.x1-k.x1)<0.3 and abs(r.y1-k.y1)<0.3 for k in DELEXACT):
            edits.append((o[0],o[1],b"")); ndel+=1; continue
        if o[3]==b"S" and len(o[6])==2 and all(abs(a-b)<1e-6 for a,b in zip(o[5],BASE)) and any(overlaps(r,z) for z in DEL):
            pts=[(1684-y, 1191-x) for x,y in o[6]]
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
    for t in texts:
        if t[2] is None: continue
        px,py=t[2]; dp=pymupdf.Point(1684-py, 1191-px)
        if any(z.contains(dp) for z in TEXTDEL):
            edits.append((t[0],t[1],b"")); ntxt+=1
    out=bytearray(); pos=0
    for a,b,rep in sorted(edits):
        if a<pos: continue
        out+=data[pos:a]; out+=rep; pos=b
    out+=data[pos:]
    doc.update_stream(xrefs[0],bytes(out))
    for x in xrefs[1:]: doc.update_stream(x,b"\n")
    return ndel,nclip,ntxt
