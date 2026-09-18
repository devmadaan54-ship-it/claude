import pymupdf
from csedit import edit_page
from plan import *
import math
SRC="proposed.pdf"; OUT="Proposed_Floor_Plan-20260916-R26.pdf"
doc=pymupdf.open(SRC); orig=pymupdf.open(SRC)
R_=pymupdf.Rect
T_GF=pymupdf.Matrix(1,0,0,1,0,0)
T_FF=pymupdf.Matrix(1.1889,0,0,1.1889,3.6,154.5-1.1889*210.9)
T_SF=pymupdf.Matrix(1.2264,0,0,1.2264,-4.0,136.7-1.2264*210.9)
def TR(r,T): 
    r=R_(r)*T; r.normalize(); return r
def toilet_symbols(S, wc=None, basin=None, shower=None):
    """place GF toilet symbols: each arg = (rot_deg, cx, cy) target in GF coords"""
    if wc: S.replay(lambda it: R_(240,411.2,300,458).contains(it["drect"]) and purple(it), rot(270,430,wc[0],wc[1],wc[2]))
    if basin: S.replay(lambda it: R_(298,411.2,331,470).contains(it["drect"]) and purple(it), rot(316,452,basin[0],basin[1],basin[2]))
    if shower: S.replay(lambda it: R_(170.5,455,235,501).contains(it["drect"]) and purple(it), rot(200,478,shower[0],shower[1],shower[2]))
def bed(S, x, y, side=True):
    """GF bed symbol (head at top) placed with head-centre top-left corner at (x,y): bed 100x106"""
    S.replay(lambda it: R_(229,230.3,335,366).contains(it["drect"]) and it["type"]!="f", pymupdf.Matrix(1,0,0,1,x-232,y-230.4))
    if side: S.rect(x-22,y,x-2,y+20); S.rect(x+102,y,x+122,y+20)
COLS=[(250,928),(440,928),(720,928),(250,775),(440,775)]             # external columns in the drive: front line + back line clear of the light well
LOGCOLS=[(522,754),(702,754),(813,754)]                              # loggia edge columns; the 11'-6" middle bay is centred on the front door
def columns(S,dashed=False):
    for cx,cy in COLS+LOGCOLS:
        if dashed: S.rect(cx-6,cy-6,cx+6,cy+6,BLACK,0.48,dashes="[2 1] 0")
        else: S.rect(cx-6,cy-6,cx+6,cy+6,BLACK,0.72,GREY)
# ---- corrected main stair: quarter turn, climbs SOUTH then turns CLOCKWISE and climbs WEST ----
CORE_DEL=[(828,748,895,876),(1008,748,1074,876),(898,871,1012,938),(929,720,970,742)]  # architect's two flights, their arrows and the dashed north landing
F1=(830.0,763.1,892.7,935.4)      # flight 1, east bay, 13 R climbing south
LND=(830.0,689.5,892.7,763.1)     # quarter landing at +8'-5"
F2=(892.7,700.4,935.9,763.1)      # flight 2, 4 R climbing west into the floor above
def cw_arrow(S,cx,cy,r,a0,a1,color=MAG,w=0.9):
    pts=[(cx+r*math.cos(math.radians(a0+(a1-a0)*i/18.0)),cy+r*math.sin(math.radians(a0+(a1-a0)*i/18.0))) for i in range(19)]
    for a,b in zip(pts,pts[1:]): S.line(a[0],a[1],b[0],b[1],color,w)
    (px,py),(qx,qy)=pts[-2],pts[-1]
    dx,dy=qx-px,qy-py; n=math.hypot(dx,dy) or 1.0; ux,uy=dx/n,dy/n
    S.poly([(qx,qy),(qx-10*ux+4.5*uy,qy-10*uy-4.5*ux),(qx-10*ux-4.5*uy,qy-10*uy+4.5*ux)],color,0,color)
DSH="[2 2] 0"
def core_stair(S):
    """flight 1 solid below the 4'-0" cut, the rest of the run dashed above it"""
    S.stair(830.0,878.0,892.7,935.4,4,'up')                                  # below the cut plane
    S.stair(830.0,763.1,892.7,878.0,8,'up',dashes=DSH,arrow=False)           # above the cut plane
    S.rect(*LND,MAG,0,dashes=DSH); S.stair(*F2,3,'right',dashes=DSH)
    cw_arrow(S,892.7,763.1,46,180,270)
    S.small("CLOCKWISE",850,706,3.0,color=MAG)
def courtyard_void(S, label=True):
    S.rect(655,512,743,655,BLACK,0.72)                    # slab edge of the void
    S.line(655,512,743,655,FURN,0.24); S.line(655,655,743,512,FURN,0.24)
    S.rect(652,509,746,658,FURN,0.48)                     # glass balustrade line
    if label: S.text("COURTYARD VOID",699,578,6.0); S.text("OPEN TO SKY",699,585,4.6); S.small("GLASS BALUSTRADE",699,591,3.0)
def ne_wing(S, y0, y1, bedname, tdim, gdim, bdim, corr_y1):
    """north extension rooms east of the living: NE garden, bedroom, toilet, corridor. y0=wall line (start), y1=outer face."""
    yi=y1-11.7                                            # inner face of north wall
    S.wall(150.1,y0,163.8,y1); S.wall(150.1,yi,557.3,y1)  # east + north walls
    for a in [(163.8,y0,163.8,yi),(163.8,yi,557.3,yi),(150.1,y0,150.1,y1),(150.1,y1,557.3,y1)]: S.OL(*a)
    S.wall(270,y0,278,yi); S.OL(270,y0,270,yi); S.OL(278,y0,278,yi)              # garden | bedroom
    S.wall(468,y0,476,yi); S.OL(468,y0,468,yi); S.OL(476,y0,476,yi)              # bedroom | toilet+corridor
    S.wall(476,corr_y1,551,corr_y1+6); S.OL(476,corr_y1,551,corr_y1); S.OL(476,corr_y1+6,551,corr_y1+6)   # toilet top wall
    S.wall(551,corr_y1,557.3,yi); S.OL(551,corr_y1,551,yi)                         # toilet east... (thin)
    S.window(270,yi,468,y1); S.window(163.8,yi,262,y1)                              # north windows (garden open rail drawn as window)
    S.door(468,y0+8,476,y0+48,'y0','left')                                          # bedroom door from corridor
    S.door(500,corr_y1,540,corr_y1+6,'x1','down')                                    # toilet door
    S.door(270,y0+60,278,y0+100,'y1','right')                                        # bedroom -> garden door
    # bedroom furniture: bed head on south (y0 side)
    bed(S,325,y0+10)
    S.hatch(280,yi-70,300,yi-4,horizontal=True)                                       # wardrobe by window? (west wall)
    S.labelr(bedname,278,y0,468,yi,373,y0+150,7.0)
    # toilet
    toilet_symbols(S, wc=(180,513,yi-20), basin=(-90,513,corr_y1+22), shower=(0,500,corr_y1+60))
    S.line(476,corr_y1+40,551,corr_y1+40,FURN,0.48,dashes="[2 2] 0")
    S.text("TOILET",513,corr_y1+80,5.0); S.text(dimstr(476,corr_y1+6,551,yi),513,corr_y1+86,4.0)
    # garden
    S.circle(216,y0+95,15,FURN,0.48); S.circle(216,y0+95,10,FURN,0.24)
    for pts in ([(180,y0+40),(194,y0+37),(199,y0+48),(186,y0+52)],[(240,y0+150),(252,y0+147),(256,y0+158),(244,y0+162)]): S.poly(pts,FURN,0.48)
    S.text("N-E GARDEN",216,y0+30,5.0); S.text(dimstr(163.8,y0,270,yi),216,y0+36,4.0); S.small("OPEN TERRACE, PLANTED",216,y0+42,3.0)
    S.text("CORRIDOR",513,y0+22,4.0)

# ================= GROUND FLOOR =================
gf=doc[0]
DEL=[R_(*r) for r in [
    (170.5,230.3,421.0,352.3),(170.5,352.3,394.0,402.3),(170.5,501.0,340.0,663.5),(340.0,546.0,394.0,663.5),
    (394.0,511.5,561.0,664.2),(437.0,492.5,484.7,512.0),(439.0,496.0,482.5,539.0),(150.3,611.5,170.2,664.1),
    (70.0,378.0,148.0,404.0),(45.0,468.0,150.4,473.0),
    (582.0,513.0,746.5,636.0),(655.0,636.0,746.5,667.5),          # foyer contents -> courtyard
    (4.0,195.0,84.0,1000.0),                                      # old slanted plot line (dash-dot) along the east side
    (662.0,684.5,830.0,766.0),(500.0,684.5,585.0,766.0),          # verandah middle + old steps
    (250.0,446.0,297.0,501.0),                                    # toilet door
    (569.3,540.0,592.0,662.0),                                    # foyer console table (moved north, clear of the new closet door)
    (344.0,494.0,397.0,543.0),                                    # old bedroom-02 door leaf (opening closed, toilet door moves to the bedroom)
    (240.0,405.0,300.0,458.0),                                    # WC symbol, replayed 23 units west to clear the new toilet door
    (345.0,352.0,396.0,410.0),                                    # old kitchen north door leaf (opening absorbed into the bath lobby) from the dressing (closed)
    (150.3,262.0,170.3,360.0),                                    # kitchen east window -> glazed door to the terrace
    (838.0,893.0,896.0,918.0),                                    # "STORE CAN BE PLANNED UNDER THE STAIRCASE" note, re-set with the new flight
    (450.0,828.0,495.0,848.0),                                    # "PORCH 47'-6 X 16'-0" label, re-set as the ramped drive
    (193.0,930.0,252.0,944.0),(170.0,958.0,275.0,968.0),          # old "MAIN ENTRANCE" / "SLIDING GATE WITH WICKET GATE"
]+CORE_DEL]
PRED=[lambda r,op,n: n==2 and r.height<0.6 and r.x0<82 and r.width>60 and 205<r.y0<1100,     # porch / side-yard paving lines
      lambda r,op,n: n==2 and r.height>300 and r.x1<110 and r.x0>20]                            # slanted boundary lines
print("GF:",edit_page(doc,gf,DEL,KEEP=[R_(402.1,511.8,437.4,511.8)],PRED=PRED))
S=Sheet(gf,orig[0])
S.door(437.4,492.9,484.3,511.8,'x0','down'); S.OL(394.3,511.8,402.1,511.8); S.OL(394.3,663.9,402.1,663.9)
CD=31.6
S.rect(170.0,230.4,201.6,296.0); S.rect(170.0,344.0,201.6,402.8); S.rect(201.6,230.4,420.4,230.4+CD)
hx0,hy0=172.5,238.0; S.rect(hx0,hy0,hx0+26.5,hy0+34.0)
for dx,dy in ((7.5,8.5),(19,8.5),(7.5,25.5),(19,25.5)): S.circle(hx0+dx,hy0+dy,4.0)
sx0,sy0=174.0,362.0; S.rrect(sx0,sy0,sx0+24,sy0+34,3,PURPLE,0.24); S.rrect(sx0+3,sy0+3,sx0+21,sy0+31,2,PURPLE,0.24); S.circle(sx0+21.5,sy0+17,1.6,PURPLE,0.24)
S.rect(384.4,262.0,420.4,298.0); S.line(384.4,280,420.4,280,FURN,0.48); S.line(414.4,262,414.4,298,FURN,0.48)
S.rect(250.0,300.0,344.0,347.0); S.line(250,300,344,347,FURN,0.24); S.line(250,347,344,300,FURN,0.24)
for cy in (312,335): S.circle(353,cy,5.5)
S.labelr("KITCHEN",170,230.4,420.4,402.8,300.0,378.0); S.small("BREAKFAST ISLAND",297,325,3.2)
S.line(232.0,410.7,232.0,492.9,FURN,0.48,dashes="[2 2] 0")
# Bedroom-01 suite (R20, hotel sequence): foyer -> walk-through closet (bath off it) -> sliding screen -> garden bedroom on a glazed east wall
S.wall(249,492.9,298,500.7); S.OL(249,492.9,298,492.9); S.OL(249,500.7,298,500.7)     # old dressing door to the toilet closed
# walk-through closet 445-561.4
S.hatch(490,511.8,561.4,538); S.hatch(445,638,522,663.9); S.rect(475,578,531,598); S.small("BENCH",503,591,2.2)
S.line(561.4,520,561.4,585,FURN,0.72); S.small("MIRROR",556,552,2.2)
S.rect(569.6,515,581,585,FURN,0.48); S.small("CONSOLE",575,510,2.0)
S.text("WALK-THROUGH",503,556,4.6); S.text("CLOSET",503,562,4.6); S.small(dimstr(445,511.8,561.4,663.9),503,567,2.8); S.small("WARDROBES BOTH SIDES",503,572,2.4)
# sliding glass screen on the line of the wall stub at x=437-441
S.line(439,511.8,439,663.9,FURN,0.72); S.line(442,511.8,442,663.9,FURN,0.72); S.rect(439,560,442,612,BLACK,0.48)
S.text("SLIDING GLASS SCREEN",436,590,2.4,vertical=True)
# garden bedroom 170-437: bed on the south wall, glazed east wall between piers 1 and 2
bed(S,328,511.8,side=False); S.rect(306,511.8,326,531.8); S.small("BATH DOOR 2'-5\" FROM THE BED",300,548,2.2)
S.door(347,402.8,393,410.7,'x1','up'); S.OL(393.3,352,393.3,402.8)                                   # kitchen door reopened (old SE bedroom door)
S.wall(347,492.9,393,511.8); S.OL(347,492.9,393,492.9); S.OL(347,511.8,393,511.8)                        # old bedroom-02 door closed
S.replay(lambda it: R_(240,411.2,300,458).contains(it["drect"]) and purple(it), pymupdf.Matrix(1,0,0,1,23,0))   # WC moved west
S.rect(234.3,493.1,271.7,500.5,(1,1,1),0,(1,1,1)); S.door(234,492.9,272,500.7,'x0','up')                    # toilet door from the bedroom
S.text("VESTIBULE",392,455,3.4); S.small(dimstr(347,410.7,437,492.9),392,460,2.4); S.small("FROM THE GREAT ROOM TO",392,465,2.0); S.small("THE KITCHEN AND THE CLOSET",392,470,2.0)
S.rect(176,640,256,662); S.circle(266,625,6); S.small("DAYBED BY THE GLASS",216,668,2.2)
S.rect(330,660,410,663.9,FURN,0.48); S.small("ART / TV WALL",370,657,2.2)
S.rect(150.6,520,169.9,611.7,(1,1,1),0,(1,1,1)); S.window(150.5,520,170,611.7)
S.small("FULL-HEIGHT GLAZING, NEW LINTEL BEAM ON PIERS 1-2",160,515,2.2)
S.labelr("BEDROOM-01",170,500.7,437,663.9,250.0,580.0); S.small("GARDEN ROOM: GLAZED EAST WALL",250,592,2.4); S.small("ONTO THE PRIVATE COURT; HIGH-LEVEL",250,597,2.4); S.small("NORTH WINDOWS ONTO THE PORTE-COCHERE",250,602,2.4)
# east side: 7'-0" clear between the house and the new 10' high boundary wall (9" thick); servant quarters at grade on a separate drawing
XW=150.5-109.9; PL=XW-11.8
S.line(PL,195,PL,1000,BLACK,0.48,dashes="[6 2 1 2] 0")
S.wall(PL,207.0,XW,950.0); S.OL(PL,207,PL,950); S.OL(XW,207,XW,950)
S.wall(XW,207.0,150.5,213.0); S.OL(XW,207,150.5,207); S.OL(XW,213,150.5,213)
S.dimline(XW,196,150.5,196,size=3.6); S.small("CLEAR, HOUSE TO NEW WALL",96,203,2.4); S.small("BOUNDARY WALL 10'-0\" HIGH",96,208,2.4)
# south part of the strip: servant quarters at grade, not shown on this sheet
# glazed breakfast bay on the servant roof (floor +5'-6", ceiling +12'-6"): boundary wall east, house wall west, glass north, skylight over the open half
S.window(XW,400,150.5,405.3); S.small("CLEAR GLASS END WALL: THE TABLE FACES THE GARDEN COURT",96,412,2.2)
S.line(95.5,215,95.5,400,BLACK,0.3,dashes="[4 2] 0"); S.small("F.F. BALCONY OVER",95.5,222,2.0)
S.rect(XW+4,219,93,396,BLACK,0.48,dashes="[2 2] 0"); S.small("SKYLIGHT OVER (DASHED)",66,392,2.0)
S.rect(XW+2,215,148.5,231,FURN,0.48); S.small("SERVERY / COFFEE STATION",96,238,2.2)
S.rect(78,322,132,372,FURN,0.48); S.circle(70,334,5); S.circle(70,360,5); S.circle(140,334,5); S.circle(140,360,5); S.small("TABLE FOR 4, GARDEN VIEW",105,382,2.0)
S.small("CLERESTORY GLASS +10'-0\" TO +12'-6\" ON THE PARK WALL",96,378,2.2)
S.wall(150.5,262,170,277); S.wall(150.5,357,170,360); S.OL(150.5,262,150.5,277); S.OL(170,262,170,277); S.OL(150.5,357,150.5,360); S.OL(170,357,170,360); S.window(150.5,277,170,298); S.window(150.5,344,170,357); S.door(150.5,298,170,344,'y1','left'); S.small("GLAZED DOOR + SIDELIGHTS IN THE EXISTING OPENING",100,362,2.0); S.small("1 R UP",132,352,2.2,color=MAG)
S.rect(58,256,146,297,(1,1,1),0,(1,1,1)); S.text("BREAKFAST BAY",96,262,4.6); S.small(dimstr(XW,213,150.5,400),96,268,2.8); S.small("GLAZED, AIR-CONDITIONED; FLOOR +5'-6\"",96,273,2.6)
S.small("1 R UP FROM THE KITCHEN; CEILING +12'-6\"",96,279,2.4); S.small("SKYLIGHT ROOF OVER THE OPEN HALF,",96,284,2.4); S.small("SOLID ROOF UNDER THE F.F. BALCONY",96,289,2.4); S.small("SERVANT QUARTERS BELOW (SHEET SQ)",96,294,2.4)
# north part: ground floor level items only
S.rect(XW+2,407,148.5,681,BLACK,0.48,dashes="[3 2] 0")
S.rect(118,410,150.5,478,FURN,0.72); toilet_symbols(S, shower=(0,132,438)); S.small("BATH DECK +5'-6\"",134,486,2.4); S.small("OUTDOOR SHOWER",134,491,2.4); S.small("FULL HT. GLAZING",134,496,2.4)
S.rect(103,611.7,150.5,664,FURN,0.48); S.small("1 R UP",126,640,2.4,color=MAG); S.rect(103,548,150.5,611.7,FURN,0.48); S.small("DECK",126,582,2.4)
S.sliding(150.5,611.7,170.0,663.9)
for yy in (500,520,540,560,580): S.rect(50,yy,68,yy+14,FURN,0.48); S.rect(74,yy,92,yy+14,FURN,0.48)
S.circle(72,645,13,FURN,0.48); S.circle(72,645,8,FURN,0.24)
S.text("BEDROOM",78,420,4.6); S.text("GARDEN COURT",78,426,4.6); S.small(dimstr(XW,405.3,150.5,683.6),78,431,2.8); S.small("ROOF GARDEN AT +5'-6\" OVER THE",78,436,2.4); S.small("ENCLOSED SERVANT UNIT; 1 R UP",78,441,2.4)
columns(S); S.small("EXTERNAL COLUMNS TO TERRACE",250,952,2.8)
# light well as a planted sunken court behind a stone parapet (option B, gate omitted); basement stair at its west end
S.rect(190.0,683.6,513.0,754.0,BLACK,0.48,dashes="[3 2] 0")
S.wall(174.3,683.6,190.0,769.7); S.wall(190.0,754.0,513.0,769.7)                      # sandstone parapet 1'-0" thick, 3'-6" high
for a in [(174.3,683.6,174.3,769.7),(190.0,769.7,513.0,769.7),(190.0,754.0,513.0,754.0),(190.0,683.6,190.0,754.0)]: S.OL(*a)
S.rect(177.4,686.7,186.9,766.6,FURN,0.24); S.rect(193.1,757.1,509.9,766.6,FURN,0.24)  # planted top recess in the parapet
S.stair(395.0,704.0,513.0,750.0,10,'left'); S.rect(345.0,704.0,395.0,750.0,MAG,0)
S.wall(345.0,683.6,391.0,689.0); S.OL(345.0,689.0,391.0,689.0)                        # stone cheek wall, no gate
S.text("DN 11 R",460,731,4.6,color=MAG); S.small("TO THE BASEMENT, LANDING AT THE DOOR BELOW",460,741,2.4,color=MAG)
S.circle(247,718,20,FURN,0.48); S.circle(247,718,13,FURN,0.24); S.circle(247,718,3,FURN,0.48)
for cx in (203,292,334):
    S.circle(cx,699,7,FURN,0.24); S.circle(cx,741,7,FURN,0.24)
S.text("SUNKEN GARDEN COURT",268,732,4.6); S.text(dimstr(190,683.6,513,754),268,739,3.4)
S.small("PLANTED, CHAMPA FROM THE WELL FLOOR",268,745,2.6)
S.small("SANDSTONE PARAPET 3'-6\" HIGH, PLANTED TOP RECESS, NO GATE; STONE CHEEK WALL TO THE FLIGHT",351,777,2.6)
# concealed event gate on east boundary (porch length)
S.line(XW,683.6,XW,940,RED,1.6,dashes="[6 3] 0")
S.text("CONCEALED EVENT GATE",100,880,4.6,color=RED); S.text("FLUSH WALL PANELS, PARK SIDE",100,886,3.4,color=RED); S.small("BOUNDARY WALL 10'-0\" HIGH",100,891,2.6,color=RED)
S.rect(XW,942,XW+157,950,MAG,0); S.text("CAR GATE 10'-0\"",120,960,4.6,color=MAG); S.small("NO COLUMN WITHIN THE GATE OR THE DRIVE LINE",120,965,2.6,color=MAG)
# pergola in west garden
x0,y0,x1,y1=1026,245,1102,382; S.rect(x0,y0,x1,y1,FURN,0.48); x=x0+5
while x<x1: S.line(x,y0,x,y1,FURN,0.24); x+=5
S.text("PERGOLA",1064,395,5.0); S.text("LOUNGE",1064,401,5.0)
# courtyard-01 (open to sky, tree) in the old stair shaft = the Brahmasthan kept open; no stair here
S.rect(655,512,743,655,FURN,0.48); S.rect(658,515,740,652,FURN,0.24)
S.circle(699,583,22,FURN,0.48); S.circle(699,583,15,FURN,0.24); S.circle(699,583,3,FURN,0.48)
for gx in range(662,740,9):
    for gy in range(519,652,9): S.line(gx,gy,gx+1,gy+1,FURN,0.3)
S.text("COURTYARD-01",699,630,6.0); S.text(dimstr(655,512,743,655),699,637,4.6); S.small("OPEN TO SKY THROUGH ALL FLOORS",699,643,3.0); S.small("TREE IN 3'-0\" DEEP PLANTER, WATERPROOFED",699,648,3.0)
S.text("ENTRANCE",612,585,5.0); S.text("FOYER",612,591,5.0); S.text(dimstr(569.3,512,655,668.4),612,597,3.8)
# grand entrance: the drive itself ramps 1:13 up to the house, so the only risers are the two at the door
S.rect(513,683.6,819,754,FURN,0.48); S.rect(516,686.6,816,751,FURN,0.24)
S.stair(518,754,706,785,2,'up'); S.text("UP 2 R",740,772,4.6,color=MAG)
S.text("ENTRANCE LOGGIA  +5'-0\"",612,714,5.6); S.text(dimstr(513,683.6,819,754),612,722,3.8)
S.small("4'-6\" DEEP, RUNNING FROM THE FRONT DOOR WEST TO THE LOBBY; COLUMNS ON ITS EDGE CARRY THE FIRST-FLOOR WING",612,728,2.6)
S.small("ENTRANCE DOOR WIDENED TO 6'-0\" DOUBLE DOOR (NEW LINTEL)",625,678,2.4)
for cx,lv in ((218,"+2'-0\""),(318,"+2'-6\""),(418,"+3'-0\""),(519,"+3'-6\""),(619,"+4'-0\""),(719,"+4'-6\""),(819,"+5'-0\"")):
    S.line(cx,812,cx,936,BLUE,0.24,dashes="[2 3] 0"); S.small(lv,cx,941,2.6,color=BLUE)
S.text("RAMPED ARRIVAL DRIVE",430,908,6.0); S.text("+1'-6\" AT THE CAR GATE TO +5'-0\" AT THE LOBBY, CONTINUOUS 1:13",430,917,4.0)
S.small("NO STEP ANYWHERE ON THE DRIVE; AT THE FRONT-DOOR AXIS IT STANDS AT +3'-11\", SO THE FLIGHT IS TWO RISERS OF 6 1/2\", 12'-0\" WIDE",430,923,2.8)
S.rect(580.6,942,643.4,950,MAG,0); S.text("PEDESTRIAN GATE 4'-0\"",612,969,4.6,color=MAG); S.small("ON THE FRONT-DOOR AXIS, NORTH PADA 'BHALLAT'",612,974,2.6,color=MAG)
# lobby core: corrected stair, arrival lobby off the drive, lift lobby in the west bay
core_stair(S)
S.rect(830.0,763.1,892.7,870.0,FURN,0.48,dashes="[2 2] 0"); S.small("STORE UNDER",861,800,2.6); S.small("THE FLIGHT",861,805,2.6)
S.wall(830.0,866.0,842.0,880.0); S.wall(830.0,928.0,842.0,942.0)                      # recessed stone portal jambs
for a in [(830,866,830,880),(842,866,842,880),(830,928,830,942),(842,928,842,942),(842,880,842,928)]: S.OL(*a)
S.line(830,880,830,928,BLUE,0.72)
S.text("ARRIVAL LOBBY",975,888,5.0); S.text(dimstr(892.7,873,1072.8,935.4),975,895,3.8)
S.small("RECESSED STONE PORTAL 4'-0\" OPEN TO THE DRIVE, THRESHOLD LEVEL AT +5'-0\"",975,901,2.6)
S.text("UP 17 R",975,916,4.6,color=MAG)
S.small("13 R CLIMBING SOUTH TO THE LANDING AT +8'-5\", THEN A CLOCKWISE QUARTER TURN",975,923,2.6,color=MAG)
S.small("AND 4 R CLIMBING WEST INTO THE FIRST FLOOR. 17 R AT 7 3/4\" X 11\".",975,928,2.6,color=MAG)
S.text("INNER LOBBY",975,730,4.6); S.text(dimstr(830,683.6,1072.8,763.1),975,737,3.4)
S.small("FROM THE VESTIBULE, UNDER THE LANDING (CLEAR 7'-7\")",975,743,2.6)
S.text("LIFT LOBBY",1042,800,4.0,color=None) if False else S.small("LIFT LOBBY, WEST BAY",1042,812,3.0)
S.line(1010.2,763.1,1010.2,935.4,FURN,0.48,dashes="[2 2] 0")
# notes
S.notes(["NOTES (REVISION R26):",
          "A. EAST SIDE: 7'-0\" CLEAR BETWEEN THE HOUSE AND THE NEW STRAIGHT 10'-0\" HIGH BOUNDARY WALL (9\" THICK), FULL LENGTH. NO OPENINGS TO THE PARK EXCEPT THE EVENT GATE; CAR GATE 10'-0\" AT THE EAST END OF THE NORTH BOUNDARY.",
          "B. CONCEALED EVENT GATE IN THE EAST BOUNDARY WALL FROM THE HOUSE CORNER TO THE FRONT BOUNDARY: FLUSH WALL-FINISHED PANELS ON CONCEALED PIVOTS, OPENED ONLY FOR EVENTS.",
          "C. BEDROOM-01 AS A HOTEL SUITE: THE OLD VESTIBULE OFF THE GREAT ROOM IS KEPT; THE OLD KITCHEN DOOR IN IT BECOMES THE BEDROOM-01 ENTRY INTO THE WALK-THROUGH CLOSET (WARDROBES BOTH SIDES), THEN THE SLIDING GLASS SCREEN AND THE GARDEN BEDROOM: BED ON THE SOUTH WALL (HEAD SOUTH), DAYBED AT THE GLAZED EAST WALL BETWEEN PIERS 1 AND 2 ONTO THE PRIVATE GARDEN COURT (NEW RCC LINTEL BEAM ON THE PIERS, TO STRUCTURAL DESIGN), HIGH-LEVEL NORTH WINDOWS ONTO THE PORTE-COCHERE. THE TOILET IS ENTERED FROM INSIDE THE BEDROOM BY A NEW 2'-5\" DOOR IN ITS NORTH WALL (WC SHIFTED WEST); THE OLD BEDROOM-02 DOOR TO THE VESTIBULE IS CLOSED. THE KITCHEN KEEPS ITS DOOR FROM THE VESTIBULE. COURTYARD-01 IN THE EXISTING STAIRWELL SHAFT, OPEN TO SKY THROUGH ALL FLOORS; THE CENTRE STAYS FREE OF STAIRS. BASEMENT STAIR IN THE LIGHT WELL; THE LIFT SERVES GROUND TO TERRACE.",
          "D. EAST STRIP: SERVANT QUARTERS AT GRADE (SHEET SQ). THEIR ROOF AT +5'-6\" CARRIES A GLAZED BREAKFAST BAY OFF THE KITCHEN, ONE RISER UP THROUGH A GLAZED DOOR WITH SIDELIGHTS IN THE OLD WINDOW OPENING: PARK WALL TO +10'-0\" WITH CLERESTORY GLASS TO THE CEILING AT +12'-6\", CLEAR GLASS END WALL TO THE GARDEN COURT WITH THE TABLE SET AGAINST IT (THE COURT PLANTING SCREENS THE BEDROOM GLAZING), SKYLIGHT ROOF OVER THE OPEN HALF AND A SOLID ROOF UNDER THE EXISTING 3'-6\" FIRST-FLOOR BALCONY; AIR-CONDITIONED, KITCHEN EXHAUST THROUGH THE ROOF. PRIVACY FROM THE PARK BY THE WALL AND THE FROSTED BANDS. NORTH OF IT THE STRIP IS BEDROOM-01'S PRIVATE GARDEN COURT: A ROOF GARDEN AT +5'-6\" ON THE SERVANT UNIT'S CONTINUOUS SLAB, ONE RISER UP FROM THE BEDROOM AND BATHROOM DOORS, WITH THE OUTDOOR SHOWER DECK AND PLANTERS.",
          "E. SERVICE WING ROOFED AT 7'-6\" WITH A PLANTER PARAPET; BATHROOM EAST WINDOW IN OBSCURE GLASS. THE WHOLE BLOCK OVER THE PORCH (LOBBY, LIFT, MAIN STAIR, UPPER LIVING ROOMS) IS DEMOLISHED AND REBUILT ON THE NEW COLUMN GRID; LIFT AND MAIN STAIR STAY IN THE NORTH-WEST.",
          "H. GRAND ENTRANCE: THE ARRIVAL DRIVE ITSELF RAMPS CONTINUOUSLY AT 1:13 FROM +1'-6\" AT THE CAR GATE TO +5'-0\" AT THE LOBBY, LEVELS MARKED EVERY 6\"; THERE IS NO STEP ON THE DRIVE OR THE WALK. AT THE FRONT-DOOR AXIS THE DRIVE STANDS AT +3'-11\", SO THE ONLY FLIGHT IS TWO RISERS OF 6 1/2\", 12'-0\" WIDE, ONTO THE ENTRANCE LOGGIA AT +5'-0\". THE LOGGIA IS 4'-6\" DEEP AND RUNS FROM THE FRONT DOOR WEST TO THE LOBBY, ITS EDGE COLUMNS CARRYING THE FIRST-FLOOR WING, THE MIDDLE BAY 11'-6\" WIDE CENTRED ON THE DOOR. CAR GATE 10'-0\" STAYS AT THE EAST END; A NEW 4'-0\" PEDESTRIAN GATE SITS ON THE DOOR AXIS IN THE NORTH PADA 'BHALLAT'. THE LIGHT WELL KEEPS THE BASEMENT FLIGHT BUT IS SCREENED FROM THE DRIVE BY A SANDSTONE PARAPET 3'-6\" HIGH WITH A PLANTED TOP RECESS AND A CHAMPA RISING OUT OF IT; NO GATE.",
          "J. MAIN STAIR, VASTU: THE CORE SITS IN THE NORTH-WEST NINTH OF THE PLOT, WHICH IS PERMITTED, AND CLEAR OF THE BRAHMASTHAN. THE ARCHITECT'S DOG-LEG TURNED CLOCKWISE BUT ITS FIRST FLIGHT CLIMBED NORTHWARD, SO THE WHOLE ASCENT RAN WEST TO EAST. IT IS RE-PLANNED AS A QUARTER-TURN: 13 RISERS UP THE EAST BAY CLIMBING SOUTH FROM THE ARRIVAL LOBBY, A 4'-0\" X 4'-8\" LANDING AT +8'-5\", THEN A CLOCKWISE TURN AND 4 RISERS CLIMBING WEST INTO THE FLOOR ABOVE. 17 RISERS (ODD) AT 7 3/4\" X 11\". BOTH LEGS NOW CLIMB IN THE FAVOURED SENSE, NORTH TO SOUTH AND EAST TO WEST, THE TURN IS CLOCKWISE (MARKED ON PLAN), AND ONLY A STORE SITS UNDER THE FLIGHT. THE WEST BAY IS FREED AS THE LIFT LOBBY AND THE GROUND-LEVEL LINK FROM THE VESTIBULE TO THE ARRIVAL LOBBY, PASSING UNDER THE LANDING AT 7'-7\" CLEAR.",
          "G. ACCESS CHECK, GROUND FLOOR: DRIVE > TWO RISERS > ENTRANCE LOGGIA > FRONT DOOR > ENTRANCE FOYER > GREAT ROOM > VESTIBULE > (SOUTH) KITCHEN, (NORTH) BEDROOM-01 CLOSET > SLIDING SCREEN > BEDROOM-01 > TOILET. KITCHEN > EAST GLAZED DOOR > BREAKFAST BAY. POWDER ROOM FROM THE FOYER. VESTIBULE > INNER LOBBY > WEST BAY > LIFT AND ARRIVAL LOBBY > MAIN STAIR, ALL UNDER COVER. DRIVE > LOBBY PORTAL > ARRIVAL LOBBY, LEVEL. LOGGIA > INNER LOBBY BY THE EXISTING DOOR. SERVANT UNIT FROM THE PORCH END ONLY. BASEMENT FROM THE LIGHT WELL FLIGHT, REACHED OFF THE LOGGIA. NO ROOM IS REACHED THROUGH ANOTHER BEDROOM OR FROM OUTDOORS.",
          "F. ALL ROOM DIMENSIONS ARE CLEAR INTERNAL SIZES TAKEN FROM THE DRAWN WALLS. SHEET ORIENTATION: TOP = SOUTH, BOTTOM = NORTH, LEFT = EAST, RIGHT = WEST."],150.5,990,5.0,maxw=1195)
S.commit()

# ================= FIRST FLOOR (page 1) =================
ff=doc[1]
DELF=[TR(r,T_FF) for r in [(166,505,428,718),(575,512,744,667),(930,505,1057,664),(556,762,571,800)]+CORE_DEL]
DELX=[TR(r,T_FF) for r in [(557.3,728.1,569.1,763.3)]]
print("FF:",edit_page(doc,ff,DELF,DELEXACT=DELX))
F=Sheet(ff,orig[0],T_FF)
courtyard_void(F); F.text("GALLERY",612,585,5.0); F.text('5\'-6" WIDE',612,591,4.0)
# study + puja in NE room
F.wall(163.8,640,252,646); F.wall(252,646,258,720.2)
for a in [(163.8,640,258,640),(163.8,646,252,646),(252,646,252,720.2),(258,640,258,720.2)]: F.OL(*a)
F.door(252,660,258,695,'y0','right')
F.rect(166,662,178,700,FURN,0.48); F.small("ALTAR",172,706,2.8)
F.text("PUJA",210,680,5.0); F.text(dimstr(163.8,646,252,720.2),210,686,4.0)
F.rect(300,560,362,592); F.circle(331,604,6); F.hatch(270,700,425,720.2)           # desk, chair, book wall
F.rrect(180,540,240,570,4); F.circle(258,555,8)                                       # cosy sofa + table
F.rect(380,510,425,528,FURN,0.48); F.small("MEMENTO SHELVES",402,536,2.8)
F.labelr("STUDY / MEMENTO ROOM",163.8,502.8,430.9,720.2,300.0,640.0)
F.small("VIDEO-CALL WALL: EAST FACING",300,660,3.0)
# master walk-in closet in former west terrace
F.hatch(930,505,1057,528); F.hatch(930,644,1057,667); F.rect(972,570,1015,600); F.small("ISLAND",993,606,2.8)
F.door(920.7,560,928.5,600,'y0','left')                                             # closet -> bathroom
F.labelr("WALK-IN CLOSET",928.5,502.8,1058.5,669.9,993.0,588.0,7.0)
# lobby core: the same corrected flight repeats, first to second floor
core_stair(F)
F.rect(830.0,763.1,892.7,861.7,FURN,0.24,dashes="[1 2] 0"); F.small("VOID OVER THE FLIGHT BELOW",861,815,2.6)
F.rect(892.7,700.4,935.9,763.1,FURN,0.24,dashes="[1 2] 0")
F.text("GALLERY + LIFT LOBBY",1042,902,4.6); F.small("BALUSTRADE TO THE STAIRWELL",1042,908,2.8)
# north-east wing over porch
columns(F)
ne_wing(F,728.1,935.8,"BEDROOM-03",'4\'-9" X 8\'-10"','6\'-9" X 12\'-5"','12\'-1" X 12\'-5"',779)
F.wall(557.3,728.1,569.1,733); F.door(557.3,733,569.1,779,'y0','right'); F.wall(557.3,779,569.1,785)
F.door(170,720.2,212,728.1,'x0','down')                                              # study -> garden (in existing window opening)
for gx0,gx1 in ((344.7,399.6),(438.8,516.8)):
    F.wall(gx0,720.2,gx1,728.1); F.OL(gx0,720.2,gx1,720.2); F.OL(gx0,728.1,gx1,728.1)   # former windows now internal: infilled
F.notes(["NOTES (FIRST FLOOR, R26):","1. THE BLOCK OVER THE PORCH IS REBUILT FROM SCRATCH ON RCC COLUMNS FROM FOUNDATION TO TERRACE: THREE ON THE FRONT (NORTH) LINE, TWO IN THE DRIVE CLEAR OF THE LIGHT WELL AND THE PARAPET, AND THREE ON THE ENTRANCE LOGGIA EDGE, NONE WITHIN THE 10'-0\" CAR GATE, THE PEDESTRIAN GATE OR THE DRIVE LINE, AND NONE ON THE FRONT-DOOR AXIS. INDEPENDENT OF THE STONE WALLS; TO STRUCTURAL DESIGN.",
          "2. FORMER WEST TERRACE ENCLOSED AS MASTER WALK-IN CLOSET (LIGHT PARTITIONS ON EXISTING SLAB). 3. NORTH-EAST ROOM RE-PURPOSED AS STUDY WITH PUJA IN ITS NORTH-EAST CORNER.",
          "4. COURTYARD VOID WITHIN THE EXISTING STAIRWELL SHAFT; GLASS BALUSTRADE. 5. ROOM DIMENSIONS ARE CLEAR INTERNAL SIZES FROM THE DRAWN WALLS."],150.1,1000,5.0,maxw=1000)
F.commit()

# ================= SECOND FLOOR (page 2) =================
sf=doc[2]
DELS=[TR(r,T_SF) for r in CORE_DEL+[(104,225,256,396),(266,225,431,396),(165,406,431,745),(447,509,561,751),(447,225,721,493),(575,512,744,667),(556,762,571,812),(214,278,266,336),(398,390,450,470),(572,700,816,932),(257,222,265,296),(257,341,265,399),(95,397.5,345.5,405),(401,397.5,445.5,405),(432.5,403.5,445.5,441)]]
DELXS=[TR(r,T_SF) for r in [(557.5,690.8,569.2,763.3)]]
print("SF:",edit_page(doc,sf,DELS,DELEXACT=DELXS))
G=Sheet(sf,orig[0],T_SF)
courtyard_void(G); G.text("FAMILY GALLERY",612,585,5.0); G.small("FAMILY PICTURES ON",612,591,3.0); G.small("COURTYARD-LIT WALL",612,596,3.0)
# restore wall face lines where partitions removed (main N-S wall stays as piers)
G.OL(444.8,398.3,444.8,404.2)
# lounge furniture
G.rrect(300,470,420,505,5); G.rrect(300,515,332,585,5); G.circle(370,545,18); G.rrect(430,560,470,600,5)
G.rect(470,300,700,330,FURN,0.48); G.small("BAR / PANTRY",585,340,3.2)
G.rrect(500,380,640,415,5); G.circle(560,445,16)
G.labelr("LOUNGE / COMMON AREA",162.2,404.2,433.1,747.6,300.0,660.0)
G.rrect(120,250,250,285,5); G.rrect(120,300,152,370,5); G.circle(200,330,18); G.rrect(300,300,340,340,5)
G.labelr("LIVING (BEST VIEW)",101.5,222.7,433.1,398.3,270.0,380.0,7.0); G.small("SEMI-OPEN: SLIDING GLASS + SCREENS TO THE EAST BALCONY",270,396,2.8)
G.labelr("COMMON LOUNGE",444.8,222.7,723.3,495,585.0,470.0,7.0)
# north wall junctions: former windows -> glazed door to garden, bedroom door from lounge, infill by corridor
G.door(165,753.5,215,759.4,'x0','down')
G.door(350,753.5,392,759.4,'x1','down')
G.wall(444.8,753.5,557.5,759.4); G.OL(444.8,753.5,557.5,753.5); G.OL(444.8,759.4,557.5,759.4)
G.wall(150.4,747.6,163.8,759.4)
G.small("EXISTING PIER LINE RETAINED, WIDE OPENING WITH LINTEL",438,470,2.6)
G.text("LUGGAGE /",504,620,5.0); G.text("STORE",504,626,5.0); G.text(dimstr(444.8,506.7,563.3,753.5),504,632,4.0)
# open view deck on external columns (no walls), railing on the north and east edges
G.rect(150.1,759.4,557.3,935.6,FURN,0.48); G.rect(150.1,930,557.3,935.6,BLACK,0.48); G.rect(150.1,759.4,155.7,935.6,BLACK,0.48)
columns(G)
G.rrect(200,800,330,834,5); G.rrect(200,845,232,915,5); G.circle(300,880,18); G.rrect(400,800,520,834,5)
G.labelr("VIEW DECK",150.1,759.4,557.3,935.6,353.0,890.0); G.small("OPEN, ON EXTERNAL COLUMNS; RAILING 3'-6\"; TERRACE SLAB OVER",353,906,3.0)
G.wall(557.5,690.8,569.2,935.6); G.OL(557.5,690.8,557.5,935.6)
# bedroom-02 with en-suite in the former living over the porch (north-west)
G.wall(569.2,683.6,723.3,689.0); G.OL(569.2,689,723.3,689)
G.door(590,683.6,632,689.0,'x0','down')
G.wall(734,846,740,935.6); G.wall(740,846,818.2,852)
for a in [(734,846,734,935.6),(740,852,740,935.6),(740,846,818.2,846),(740,852,818.2,852)]: G.OL(*a)
G.door(740,858,818.2,864,'x0','down') if False else G.door(734,870,740,905,'y0','left')
toilet_symbols(G, wc=(90,800,925), basin=(90,760,925), shower=(0,750,870))
G.text("EN-SUITE",779,905,4.0); G.text(dimstr(740,852,818.2,935.6),779,910,3.4)
bed(G,640,700); G.hatch(572,700,592,840)
G.labelr("BEDROOM-02",569.2,689,818.2,935.6,690.0,900.0,7.0)
core_stair(G)
G.rect(830.0,763.1,892.7,861.7,FURN,0.24,dashes="[1 2] 0"); G.small("VOID OVER THE FLIGHT BELOW",861,815,2.6)
G.rect(892.7,700.4,935.9,763.1,FURN,0.24,dashes="[1 2] 0")
G.text("GALLERY + LIFT LOBBY",1042,902,4.6)
G.notes(["NOTES (SECOND FLOOR, R3):","1. SOUTH-EAST TOILET, WALK-IN CLOSET AND BEDROOM-02 REMOVED; THE SOUTH-EAST CORNER WITH THE BEST VIEW BECOMES THE LIVING ROOM, THE REST A COMMON LOUNGE. FORMER NORTH WINDOWS BECOME DOORS TO THE GARDEN AND BEDROOM-02, OR ARE INFILLED.",
          "2. BEDROOM-02 WITH EN-SUITE IN THE FORMER LIVING OVER THE PORCH (NORTH-WEST); THE NEW EAST WING AT THIS LEVEL IS AN OPEN VIEW DECK ON EXTERNAL COLUMNS, NO WALLS. 3. STRUCTURAL WALL LINES RETAINED AS PIERS; OPENINGS WITH LINTELS.",
          "4. FAMILY GALLERY ALONG THE COURTYARD VOID. 5. ROOM DIMENSIONS ARE CLEAR INTERNAL SIZES FROM THE DRAWN WALLS."],150.4,1000,5.0,maxw=970)
G.commit()

# ================= BASEMENT (copy of GF template) =================
def template(title1,title2,drg):
    doc.fullcopy_page(0); pg=doc[len(doc)-1]
    PLAN=[R_(34,26,1640,1166)]; TXT=[R_(34,26,1640,1166), R_(1390,630,1600,675), R_(1396,828,1470,846)]
    edit_page(doc,pg,PLAN,TEXTDEL=TXT)
    Sx=Sheet(pg,orig[0])
    Sx.text(title1,1392.8,648.0,17.09,align="left",fontpath=ARIALB); Sx.text(title2,1392.4,668.5,17.09,align="left",fontpath=ARIALB); Sx.text(drg,1398.1,840.5,14.12,align="left",fontpath=ARIAL)
    return pg,Sx
bf,B=template("BASEMENT -","RENOVATION LAYOUT","BF-PP-01")
exec(open("basement_layout.py").read())
B.commit()

# ================= TERRACE FLOOR =================
tf,Tt=template("TERRACE FLOOR -","LAYOUT","TF-PP-01")
X0,X1,Y0,Y1=150.1,1084.6,210.9,947.3
Tt.wall(X0,Y0,X1,Y0+6); Tt.wall(X0,Y0,X0+6,Y1); Tt.wall(X1-6,Y0,X1,Y1); Tt.wall(X0,Y1-6,X1,Y1)   # parapet
Tt.wall(95.6,222.7,101.5,759.4); Tt.wall(95.6,222.7,X0,228.7); Tt.wall(95.6,753.5,X0,759.4)        # east bay parapet
for a in [(X0+6,Y0+6,X1-6,Y0+6),(X0+6,Y0+6,X0+6,Y1-6),(X1-6,Y0+6,X1-6,Y1-6),(X0+6,Y1-6,X1-6,Y1-6)]: Tt.OL(*a)
# mumty: stair + lift
Tt.wall(830,683.6,1084.6,695.4); Tt.wall(830,683.6,842,947.3); Tt.wall(892.7,775,904.4,873); Tt.wall(998.5,775,1010.2,873); Tt.wall(892.7,861.2,1010.2,873)
Tt.rect(904.4,775,998.5,861.2,FURN,0.48); Tt.line(904.4,775,998.5,861.2,FURN,0.24); Tt.line(904.4,861.2,998.5,775,FURN,0.24); Tt.text("LIFT",951,822,5.0)
Tt.stair(830.0,763.1,892.7,935.4,12,'down'); Tt.rect(*LND,MAG,0); Tt.stair(892.7,700.4,935.9,763.1,3,'left')
Tt.text("DN 17 R",861,676,4.6,color=MAG); Tt.small("ASCENT CLIMBS SOUTH, THEN TURNS CLOCKWISE AND CLIMBS WEST",861,664,2.6,color=MAG)
Tt.text("STAIR + LIFT MUMTY",960,900,5.0)
Tt.wall(714,776,830,782); Tt.wall(714,782,720,941.3); Tt.wall(720,826,830,832)
for a in [(714,776,830,776),(720,782,720,941.3),(714,782,714,941.3),(720,826,830,826),(720,832,830,832)]: Tt.OL(*a)
Tt.door(830,850,842,890,'y0','left')
Tt.door(760,826,800,832,'x0','down')
toilet_symbols(Tt, wc=(-90,810,804), basin=(-90,740,804))
Tt.text("STAFF WC",772,815,3.6)
Tt.rect(726,840,768,924,FURN,0.48); Tt.line(726,858,768,858,FURN,0.48); Tt.text("STAFF ROOM",800,880,5.0); Tt.text(dimstr(720,832,830,941.3),800,886,4.0)

columns(Tt,dashed=True)
courtyard_void(Tt,label=False); Tt.text("COURTYARD VOID",699,578,6.0); Tt.text("OPEN SKYLIGHT OPENING",699,585,4.6); Tt.small("SAFETY RAILING 3'-6\" HIGH",699,591,3.0)
# ---- services enclosure, south-west (heavy, louvred screen) ----
Tt.rect(840,232,1075,336,FURN,0.72,dashes="[3 2] 0")
Tt.rect(985,240,1068,300,FURN,0.48); Tt.line(985,240,1068,300,FURN,0.24); Tt.line(985,300,1068,240,FURN,0.24); Tt.text("WATER TANKS",1026,312,4.6); Tt.small("2 X 2000 L",1026,317,2.8)
Tt.rect(905,240,975,300,FURN,0.48); Tt.circle(940,270,20); Tt.circle(940,270,6); Tt.text("CENTRAL",940,312,4.6); Tt.text("WATER HEATER",940,318,4.6); Tt.small("HEAT PUMP + SOLAR THERMAL",940,323,2.6)
for i in range(3): Tt.rect(848+i*18,244,862+i*18,270,FURN,0.48)
Tt.text("AC ODUs",876,282,4.0); Tt.small("+ PUMPS",876,287,2.6)
Tt.text("SERVICES ENCLOSURE",957,344,5.0); Tt.text(dimstr(840,232,1075,336),957,354,4.0); Tt.small("LOUVRED SCREEN, SOUTH-WEST",957,349,2.8)
# ---- solar array along the south edge ----
for i in range(10): Tt.rect(330+i*50,236,374+i*50,296,FURN,0.48); Tt.line(330+i*50,266,374+i*50,266,FURN,0.24)
Tt.text("SOLAR PV ARRAY, SOUTH EDGE (10 PANELS SHOWN, EXTEND AS REQUIRED)",580,306,4.6)
# ---- sky pavilion, semi-closed party space on the east ----
px0,py0,px1,py1=180,375,570,705
Tt.rect(px0,py0,px1,py1,BLACK,0.72)
Tt.rect(px0+3,py0+3,px1-3,py1-3,FURN,0.48)                       # sliding glass line
x=px0+8
while x<px1: Tt.line(x,py0,x,py1,FURN,0.24); x+=6                  # louvre roof
Tt.rect(px0+10,py0+12,px0+120,py0+38); Tt.text("BAR",px0+65,py0+30,4.0)
for cy in (py0+48,py0+72,py0+96): Tt.circle(px0+30,cy,5.5)
Tt.rect(px0+150,py0+20,px0+330,py0+70,FURN,0.48)
for i in range(4): Tt.circle(px0+172+i*45,py0+8,6); Tt.circle(px0+172+i*45,py0+82,6)
Tt.small("DINING 8",px0+240,py0+90,3.0)
Tt.rrect(px0+30,py0+150,px0+170,py0+184,5); Tt.rrect(px0+30,py0+200,px0+64,py0+280,5); Tt.circle(px0+120,py0+235,18); Tt.rrect(px0+180,py0+200,px0+230,py0+250,5)
Tt.rrect(px0+250,py0+150,px0+370,py0+184,5); Tt.rrect(px0+330,py0+200,px0+370,py0+280,5)
Tt.rect(px1-60,py1-50,px1-10,py1-10,FURN,0.48); Tt.small("AV / DJ",px1-35,py1-28,2.8)
Tt.text("SKY PAVILION",375,660,8.0); Tt.text(dimstr(180,375,570,705),375,669,6.0)
Tt.small("SEMI-CLOSED: RETRACTABLE LOUVRE ROOF, SLIDING GLASS + INSECT SCREENS, HEATERS",375,676,3.0)
Tt.small("OPENS ONTO THE OPEN TERRACE AND THE NORTH-EAST DECK",375,681,3.0)
# ---- guest wc by the drying yard (north-west) ----
Tt.wall(626,776,632,834); Tt.wall(632,828,708,834); Tt.wall(702,776,708,828)
for a in [(626,776,626,834),(632,776,632,828),(632,828,702,828),(632,834,708,834),(702,776,702,828),(708,776,708,834)]: Tt.OL(*a)
Tt.door(650,828,690,834,'x0','down'); toilet_symbols(Tt, wc=(-90,690,800), basin=(-90,648,800)); Tt.text("GUEST WC",667,846,3.8); Tt.text(dimstr(632,776,702,828),667,851,3.0)
Tt.rect(600,856,708,941.3,FURN,0.48,dashes="[2 2] 0"); Tt.text("CLOTHES DRYING",654,900,4.6); Tt.small("(SCREENED, NORTH-WEST)",654,906,2.8)
# ---- open terrace / north-east deck ----
Tt.rect(X0+6,Y1-40,600,Y1-6,FURN,0.48,dashes="[2 2] 0"); Tt.text("PLANTER STRIP ALONG NORTH EDGE",380,Y1-20,4.6)
Tt.rect(180,720,560,900,FURN,0.48,dashes="[3 2] 0"); Tt.text("NORTH-EAST DECK",370,810,6.0); Tt.text(dimstr(180,720,560,900),370,817,4.6); Tt.text("OPEN, LOW PLANTING, EVENT OVERFLOW",370,818,4.0)
Tt.text("OPEN TERRACE",930,520,8.0); Tt.text("PAVED, WITH THE COURTYARD VOID RAILED",930,529,4.6)
Tt.notes(["NOTES (TERRACE, R5):","1. PARAPET 3'-6\" HIGH ALL ROUND; COURTYARD VOID RAILED. 2. WATER TANKS, CENTRAL WATER HEATER, AC OUTDOOR UNITS AND PUMPS IN A LOUVRED SERVICES ENCLOSURE IN THE SOUTH-WEST; SOLAR PV ALONG THE SOUTH PARAPET; NORTH-EAST KEPT OPEN AND LOW (VASTU).",
          "3. SKY PAVILION ON THE EAST: STEEL FRAME, RETRACTABLE LOUVRE ROOF, SLIDING GLASS WITH INSECT SCREENS, BAR, DINING AND LOUNGE; POWER AND WATER TO THE BAR. 4. STAFF ROOM, WC, GUEST WC AND SCREENED DRYING YARD BESIDE THE MUMTY (NORTH-WEST).",
          "5. TERRACE SLAB OVER THE NORTH WING CARRIED ON THE EXTERNAL COLUMNS (DASHED); PAVILION AND SERVICES LOADS TO BE CHECKED BY THE STRUCTURAL ENGINEER. 6. WATERPROOFING AND SLOPES TO NORTH-EAST DRAIN POINTS."],150.1,1000,5.0,maxw=1195)
Tt.commit()

# order: BF, GF, FF, SF, TF
doc.move_page(3,0)   # basement to front
doc.save(OUT,garbage=1,deflate=True); print("saved",OUT,len(doc))
