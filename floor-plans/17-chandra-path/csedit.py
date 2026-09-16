import re, pymupdf
TOK=re.compile(rb"/[^\s/\[\]<>(){}%]*|[-+]?\d*\.?\d+|\[|\]|<<|>>|\([^)]*\)|<[0-9A-Fa-f\s]*>|[A-Za-z'\"*]+|%[^\n]*")
NUM=re.compile(rb"^[-+]?\d*\.?\d+$")
PAINT={b"S",b"s",b"f",b"F",b"f*",b"B",b"B*",b"b",b"b*",b"n"}
CONS={b"m",b"l",b"c",b"v",b"y",b"re",b"h"}
def mul(a,b):
    # matrices as (a,b,c,d,e,f); a then b
    return (a[0]*b[0]+a[1]*b[2], a[0]*b[1]+a[1]*b[3], a[2]*b[0]+a[3]*b[2], a[2]*b[1]+a[3]*b[3], a[4]*b[0]+a[5]*b[2]+b[4], a[4]*b[1]+a[5]*b[3]+b[5])
def apply(m,x,y): return (m[0]*x+m[2]*y+m[4], m[1]*x+m[3]*y+m[5])
def parse(data):
    """yield path objects: (start_offset, end_offset, bbox_pdf_unrotated(x0,y0,x1,y1), paint_op, n_ops)"""
    ctm=(1,0,0,1,0,0); stack=[]; operands=[]; objs=[]; lw=None
    cur=None  # [start, pts]
    intext=False; opstart=None
    for m in TOK.finditer(data):
        t=m.group(0)
        if opstart is None: opstart=m.start()
        if NUM.match(t): operands.append(float(t)); continue
        if t[:1] in b"/[]<(%": operands.append(t); continue
        op=t
        if op==b"q": stack.append(ctm)
        elif op==b"Q": ctm=stack.pop() if stack else ctm
        elif op==b"cm" and len(operands)>=6:
            ctm=mul(tuple(operands[-6:]),ctm)
        elif op==b"w" and operands: lw=operands[-1]
        elif op==b"BT": intext=True
        elif op==b"ET": intext=False
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
    return objs
