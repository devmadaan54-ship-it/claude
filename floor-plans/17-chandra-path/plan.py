import pymupdf, math
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
GREY=(0.55294,0.55294,0.55294); FURN=(0.70196,0.70196,0.70196); PURPLE=(0.35294,0.28627,0.61176)
BLACK=(0,0,0); BLUE=(0,0.49804,1); MAG=(0.85882,0.01176,0.98824); RED=(0.96471,0.14510,0.03529)
FONTS={}
def font(path):
    if path not in FONTS:
        f=TTFont(path); FONTS[path]=(f,f.getGlyphSet(),f.getBestCmap(),f["head"].unitsPerEm)
    return FONTS[path]
DIDACT="DidactGothicRegular.ttf"; ARIALB="/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"; ARIAL="/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

class Sheet:
    """draw on a rotated page using displayed (sheet) coordinates"""
    def __init__(self, page, src_page=None, T=None):
        self.page=page; self.D=page.derotation_matrix; self.M=page.rotation_matrix
        self.T=T or pymupdf.Matrix(1,0,0,1,0,0)
        self.sh=page.new_shape()
        self.ODR=None
        if src_page is not None:
            self.ODR=src_page.get_drawings()
            for it in self.ODR:
                r=pymupdf.Rect(it["rect"])*self.M; r.normalize(); it["drect"]=r
    def P(self,x,y): return pymupdf.Point(x,y)*self.T*self.D
    def G(self,x0,y0,x1,y1):
        a=pymupdf.Point(x0,y0)*self.T; b=pymupdf.Point(x1,y1)*self.T; return pymupdf.Rect(min(a.x,b.x),min(a.y,b.y),max(a.x,b.x),max(a.y,b.y))
    def R(self,x0,y0,x1,y1):
        a=self.P(x0,y0); b=self.P(x1,y1); return pymupdf.Rect(min(a.x,b.x),min(a.y,b.y),max(a.x,b.x),max(a.y,b.y))
    def commit(self): self.sh.commit(overlay=True)
    # primitives
    def wall(self,x0,y0,x1,y1,outline=True):
        self.sh.draw_rect(self.R(x0,y0,x1,y1)); self.sh.finish(color=GREY,fill=GREY,width=0)
    def OL(self,x0,y0,x1,y1): self.line(x0,y0,x1,y1,BLACK,0.96)
    def line(self,x0,y0,x1,y1,color=BLACK,width=0,dashes=None):
        width=width or 0.1
        self.sh.draw_line(self.P(x0,y0),self.P(x1,y1)); self.sh.finish(color=color,width=width,dashes=dashes,closePath=False)
    def rect(self,x0,y0,x1,y1,color=FURN,width=0.48,fill=None,dashes=None):
        width=width or (0.1 if color is not None else 0)
        self.sh.draw_rect(self.R(x0,y0,x1,y1)); self.sh.finish(color=color,width=width,fill=fill,dashes=dashes)
    def poly(self,pts,color=FURN,width=0.48,fill=None,close=True):
        self.sh.draw_polyline([self.P(*p) for p in pts]+([self.P(*pts[0])] if close else [])); self.sh.finish(color=color,width=width,fill=fill,closePath=close)
    def circle(self,cx,cy,r,color=FURN,width=0.48,fill=None):
        self.sh.draw_circle(self.P(cx,cy),r*self.T.a); self.sh.finish(color=color,width=width,fill=fill)
    def arc(self,cx,cy,px,py,angle,color=BLACK,width=0):
        width=width or 0.1
        self.sh.draw_sector(self.P(cx,cy),self.P(px,py),angle,fullSector=False); self.sh.finish(color=color,width=width,closePath=False)
    def rrect(self,x0,y0,x1,y1,r,color=FURN,width=0.48):
        sh=self.sh; P=self.P
        sh.draw_line(P(x0+r,y0),P(x1-r,y0)); sh.draw_sector(P(x1-r,y0+r),P(x1-r,y0),90,fullSector=False)
        sh.draw_line(P(x1,y0+r),P(x1,y1-r)); sh.draw_sector(P(x1-r,y1-r),P(x1,y1-r),90,fullSector=False)
        sh.draw_line(P(x1-r,y1),P(x0+r,y1)); sh.draw_sector(P(x0+r,y1-r),P(x0+r,y1),90,fullSector=False)
        sh.draw_line(P(x0,y1-r),P(x0,y0+r)); sh.draw_sector(P(x0+r,y0+r),P(x0,y0+r),90,fullSector=False)
        sh.finish(color=color,width=width,closePath=False)
    def hatch(self,x0,y0,x1,y1,step=2.45,horizontal=True):
        self.rect(x0,y0,x1,y1,BLACK,0.48)
        if horizontal:
            y=y0+step
            while y<y1: self.line(x0,y,x1,y,BLACK,0); y+=step
        else:
            x=x0+step
            while x<x1: self.line(x,y0,x,y1,BLACK,0); x+=step
    def window(self,x0,y0,x1,y1):
        """window in wall rect; blue lines along the wall, black end lines"""
        horiz=(x1-x0)>(y1-y0)
        if horiz:
            self.line(x0,y0,x0,y1,BLACK,0.96); self.line(x1,y0,x1,y1,BLACK,0.96)
            for f in (0,0.3,0.5,0.7,1.0): self.line(x0,y0+(y1-y0)*f,x1,y0+(y1-y0)*f,BLUE,0)
        else:
            self.line(x0,y0,x1,y0,BLACK,0.96); self.line(x0,y1,x1,y1,BLACK,0.96)
            for f in (0,0.3,0.5,0.7,1.0): self.line(x0+(x1-x0)*f,y0,x0+(x1-x0)*f,y1,BLUE,0)
    def door(self,x0,y0,x1,y1,hinge,swing):
        horiz=(x1-x0)>(y1-y0); rect=self.rect; line=self.line
        if horiz:
            line(x0,y0,x0,y1,BLACK,0.96); line(x1,y0,x1,y1,BLACK,0.96)
            rect(x0,y0,x0+3,y1,BLACK,0.48); rect(x1-3,y0,x1,y1,BLACK,0.48)
            L=(x1-x0)-6; hx=x0+3 if hinge=='x0' else x1-3
            dirn=-1 if swing=='up' else 1; yw=y0 if swing=='up' else y1
            lx0=hx if hinge=='x0' else hx-1.3
            rect(lx0,min(yw,yw+dirn*L),lx0+1.3,max(yw,yw+dirn*L),BLACK,0)
            self.arc(hx,yw,hx,yw+dirn*L, -90 if (hinge=='x0')==(swing=='up') else 90)
            line(x0+3,yw,x1-3,yw,BLACK,0)
        else:
            line(x0,y0,x1,y0,BLACK,0.96); line(x0,y1,x1,y1,BLACK,0.96)
            rect(x0,y0,x1,y0+3,BLACK,0.48); rect(x0,y1-3,x1,y1,BLACK,0.48)
            L=(y1-y0)-6; hy=y0+3 if hinge=='y0' else y1-3
            dirn=-1 if swing=='left' else 1; xw=x0 if swing=='left' else x1
            ly0=hy if hinge=='y0' else hy-1.3
            rect(min(xw,xw+dirn*L),ly0,max(xw,xw+dirn*L),ly0+1.3,BLACK,0)
            self.arc(xw,hy,xw+dirn*L,hy, 90 if (hinge=='y0')==(swing=='left') else -90)
            line(xw,y0+3,xw,y1-3,BLACK,0)
    def sliding(self,x0,y0,x1,y1):
        """sliding glass door in wall rect (vertical wall)"""
        horiz=(x1-x0)>(y1-y0)
        if horiz:
            self.line(x0,y0,x0,y1,BLACK,0.96); self.line(x1,y0,x1,y1,BLACK,0.96)
            m=(x0+x1)/2; t=(y1-y0)
            self.rect(x0+1,y0+t*0.25,m+3,y0+t*0.45,BLACK,0.48); self.rect(m-3,y0+t*0.55,x1-1,y0+t*0.75,BLACK,0.48)
        else:
            self.line(x0,y0,x1,y0,BLACK,0.96); self.line(x0,y1,x1,y1,BLACK,0.96)
            m=(y0+y1)/2; t=(x1-x0)
            self.rect(x0+t*0.25,y0+1,x0+t*0.45,m+3,BLACK,0.48); self.rect(x0+t*0.55,m-3,x0+t*0.75,y1-1,BLACK,0.48)
    def stair(self,x0,y0,x1,y1,n,direction,color=MAG,dashes=None,arrow=True):
        """flight rect with n treads, direction 'left'/'right'/'up'/'down' = direction of travel (arrow)"""
        self.rect(x0,y0,x1,y1,color,0,dashes=dashes)
        if not arrow:
            if direction in ('left','right'):
                for i in range(1,n): self.line(x0+(x1-x0)*i/n,y0,x0+(x1-x0)*i/n,y1,color,0,dashes=dashes)
            else:
                for i in range(1,n): self.line(x0,y0+(y1-y0)*i/n,x1,y0+(y1-y0)*i/n,color,0,dashes=dashes)
            return
        if direction in ('left','right'):
            for i in range(1,n): self.line(x0+(x1-x0)*i/n,y0,x0+(x1-x0)*i/n,y1,color,0,dashes=dashes)
            cy=(y0+y1)/2
            if direction=='right': self.line(x0+4,cy,x1-8,cy,color,0.48); self.poly([(x1-8,cy-3),(x1-2,cy),(x1-8,cy+3)],color,0,color)
            else: self.line(x1-4,cy,x0+8,cy,color,0.48); self.poly([(x0+8,cy-3),(x0+2,cy),(x0+8,cy+3)],color,0,color)
        else:
            for i in range(1,n): self.line(x0,y0+(y1-y0)*i/n,x1,y0+(y1-y0)*i/n,color,0,dashes=dashes)
            cx=(x0+x1)/2
            if direction=='down': self.line(cx,y0+4,cx,y1-8,color,0.48); self.poly([(cx-3,y1-8),(cx,y1-2),(cx+3,y1-8)],color,0,color)
            else: self.line(cx,y1-4,cx,y0+8,color,0.48); self.poly([(cx-3,y0+8),(cx,y0+2),(cx+3,y0+8)],color,0,color)
    # text as outlines
    def text(self,s,cx,y_base,size,align="center",color=BLACK,fontpath=DIDACT,vertical=False):
        f,gs,cmap,upm=font(fontpath); sc=size/upm; sh=self.sh
        adv=sum(f["hmtx"][cmap[ord(ch)]][0] for ch in s if ord(ch) in cmap)*sc
        x=cx-adv/2 if align=="center" else cx
        for ch in s:
            gname=cmap.get(ord(ch))
            if not gname: continue
            pen=DecomposingRecordingPen(gs); gs[gname].draw(pen)
            cur=None; start=None
            if vertical: tp=lambda pt: self.P(cx+pt[1]*sc, x+ (adv - (x-(cx-adv/2))) )  # unused
            def tp(pt): return self.P(x+pt[0]*sc, y_base-pt[1]*sc)
            for op,args in pen.value:
                if op=="moveTo": cur=args[0]; start=cur
                elif op=="lineTo": sh.draw_line(tp(cur),tp(args[0])); cur=args[0]
                elif op=="qCurveTo":
                    pts=list(args)
                    if pts[-1] is None: pts[-1]=start
                    ctrls=pts[:-1]; last=pts[-1]; p0=cur
                    for i,c in enumerate(ctrls):
                        p2=last if i==len(ctrls)-1 else ((c[0]+ctrls[i+1][0])/2,(c[1]+ctrls[i+1][1])/2)
                        prev=p0
                        for k in range(1,9):
                            t=k/8; q=((1-t)**2*p0[0]+2*(1-t)*t*c[0]+t*t*p2[0],(1-t)**2*p0[1]+2*(1-t)*t*c[1]+t*t*p2[1])
                            sh.draw_line(tp(prev),tp(q)); prev=q
                        p0=p2
                    cur=last
                elif op=="curveTo":
                    c1,c2,p3=args; sh.draw_bezier(tp(cur),tp(c1),tp(c2),tp(p3)); cur=p3
                elif op in ("closePath","endPath"):
                    if cur and start and cur!=start: sh.draw_line(tp(cur),tp(start))
                    cur=None
            sh.finish(color=None,fill=color,width=0,even_odd=False,closePath=True)
            x+=f["hmtx"][gname][0]*sc
        return adv
    def label(self,name,dims,cx,cy,size=8.0):
        self.text(name,cx,cy,size)
        if dims: self.text(dims,cx,cy+9.5,6.4)
    def small(self,s,cx,cy,size=3.2,color=BLACK): self.text(s,cx,cy,size,color=color)
    def note(self,s,x,cy,size=5.0): self.text(s,x,cy,size,align="left")
    def textw(self,s,size,fontpath=DIDACT):
        f,gs,cmap,upm=font(fontpath); sc=size/upm
        return sum(f["hmtx"][cmap[ord(ch)]][0] for ch in s if ord(ch) in cmap)*sc
    def notes(self,lines,x,y0,size=5.0,maxw=1200.0,lh=8.0):
        """left-aligned note block, wrapped to maxw sheet units, continuation lines indented"""
        for t in lines:
            cur=""; ind=x
            for w in t.split(" "):
                trial=(cur+" "+w).strip()
                if cur and self.textw(trial,size)>(maxw-(ind-x)):
                    self.note(cur,ind,y0,size); y0+=size*1.32; ind=x+size*1.6; cur=w
                else: cur=trial
            if cur: self.note(cur,ind,y0,size)
            y0+=lh
        return y0
    # replay original drawings with a transform in displayed space
    def replay(self,sel,mat):
        T=self.M*mat*self.T*self.D; n=0; sh=self.sh
        for it in self.ODR:
            if not sel(it): continue
            n+=1
            for itm in it["items"]:
                k=itm[0]
                if k=="l": sh.draw_line(itm[1]*T,itm[2]*T)
                elif k=="c": sh.draw_bezier(itm[1]*T,itm[2]*T,itm[3]*T,itm[4]*T)
                elif k=="re": sh.draw_polyline([q*T for q in itm[1].quad])
                elif k=="qu": sh.draw_polyline([itm[1].ul*T,itm[1].ur*T,itm[1].lr*T,itm[1].ll*T,itm[1].ul*T])
            sh.finish(color=it.get("color"),fill=it.get("fill"),width=it.get("width") or 0,dashes=it.get("dashes"),
                      closePath=it.get("closePath",False),even_odd=it.get("even_odd",False),
                      lineCap=max(it.get("lineCap") or (0,)) if it.get("lineCap") else 0,lineJoin=it.get("lineJoin") or 0)
        return n
def rot(cx,cy,deg,tx,ty): return pymupdf.Matrix(1,0,0,1,-cx,-cy)*pymupdf.Matrix(deg)*pymupdf.Matrix(1,0,0,1,tx,ty)
def inside(z):
    z=pymupdf.Rect(z); return lambda it: z.contains(it["drect"])
def purple(it): return bool(it.get("color")) and abs(it["color"][0]-0.35294)<0.01

def vastu_grid(S,x0,y0,x1,y1):
    """9x9 pada grid with zone labels, light red, dashed"""
    col=(0.96,0.15,0.04)
    for i in range(10):
        x=x0+(x1-x0)*i/9; S.line(x,y0,x,y1,col,0.3 if i%3 else 0.7,dashes=None if i%3==0 else "[2 3] 0")
        y=y0+(y1-y0)*i/9; S.line(x0,y,x1,y,col,0.3 if i%3 else 0.7,dashes=None if i%3==0 else "[2 3] 0")
    # sheet orientation: top=S, bottom=N, left=E, right=W
    names=[["SE","S","SW"],["E","BRAHMASTHAN","W"],["NE","N","NW"]]
    for r in range(3):
        for c in range(3):
            cx=x0+(x1-x0)*(c+0.5)/3; cy=y0+(y1-y0)*(r+0.5)/3
            S.text(names[r][c],cx,cy,7.0,color=col)
    S.text("VASTU GRID 9 X 9 PADA (ASSESSMENT OVERLAY ONLY)",x0+(x1-x0)/2,y0-6,5.0,color=col)

FT=15.7
def ftin(pts):
    inches=round(pts/FT*12)
    f,i=divmod(inches,12)
    return f"{f}'-{i}\""
def dimstr(x0,y0,x1,y1): return f"{ftin(abs(x1-x0))} X {ftin(abs(y1-y0))}"
def _labelr(self,name,x0,y0,x1,y1,cx,cy,size=8.0):
    self.text(name,cx,cy,size); self.text(dimstr(x0,y0,x1,y1),cx,cy+size*1.19,size*0.8)
Sheet.labelr=_labelr
def _dimline(self,x0,y0,x1,y1,offset=0,size=4.0):
    """dimension between two points (horizontal or vertical), text in the middle"""
    horiz=abs(x1-x0)>abs(y1-y0)
    if horiz:
        y=y0+offset; self.line(x0,y,x1,y,BLACK,0.48); self.line(x0,y-4,x0,y+4,BLACK,0.48); self.line(x1,y-4,x1,y+4,BLACK,0.48)
        self.text(ftin(abs(x1-x0)),(x0+x1)/2,y-2,size)
    else:
        x=x0+offset; self.line(x,y0,x,y1,BLACK,0.48); self.line(x-4,y0,x+4,y0,BLACK,0.48); self.line(x-4,y1,x+4,y1,BLACK,0.48)
        self.text(ftin(abs(y1-y0)),x,(y0+y1)/2,size)
Sheet.dimline=_dimline
