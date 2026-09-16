import pymupdf
from csedit import edit_page
from plan import *
SRC="proposed.pdf"; OUT="Proposed_Floor_Plan-20260916-R15.pdf"
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
COLS=[(250,928),(440,928),(630,928),(250,696),(440,696),(630,696)]   # external columns: front line + two at the back
def columns(S,dashed=False):
    for cx,cy in COLS:
        if dashed: S.rect(cx-6,cy-6,cx+6,cy+6,BLACK,0.48,dashes="[2 1] 0")
        else: S.rect(cx-6,cy-6,cx+6,cy+6,BLACK,0.72,GREY)
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
]]
PRED=[lambda r,op,n: n==2 and r.height<0.6 and r.x0<82 and r.width>60 and 205<r.y0<1100,     # porch / side-yard paving lines
      lambda r,op,n: n==2 and r.height>300 and r.x1<110 and r.x0>20]                            # slanted boundary lines
print("GF:",edit_page(doc,gf,DEL,KEEP=[R_(402.1,511.8,437.4,511.8)],PRED=PRED))
S=Sheet(gf,orig[0])
S.wall(437.4,492.9,484.3,511.8); S.OL(437.4,492.9,484.3,492.9); S.OL(437.4,511.8,484.3,511.8); S.OL(394.3,511.8,402.1,511.8); S.OL(394.3,663.9,402.1,663.9)
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
S.wall(296.0,560.0,303.9,663.9); S.OL(296,560,296,663.9); S.OL(303.9,560,303.9,663.9); S.OL(296,560,303.9,560)
S.hatch(170.0,500.7,252.0,527.0); S.hatch(270.0,560.0,296.0,663.9); S.rect(170.0,545.0,190.0,605.0); S.circle(200,575,6)
S.labelr("DRESSING",170,500.7,296,663.9,236.0,600.0)
bed(S,418,511.8,side=False); S.rect(396,511.8,416,531.8); S.rect(520,511.8,540,531.8)
S.rect(312,560,342,590); S.circle(357,575,8); S.rect(445,634,515,656); S.circle(480,624,6); S.rect(330,650,430,662)
S.labelr("BEDROOM-01",303.9,500.7,561.4,663.9,362.0,618.0)
# east side: plot line 7'-0" from the house (survey), new 10' high boundary wall 9" thick inside it -> clear strip 6'-3"
PL=41.0; XW=PL+11.8
S.line(PL,195,PL,1000,BLACK,0.48,dashes="[6 2 1 2] 0")
S.wall(PL,207.0,XW,950.0); S.OL(PL,207,PL,950); S.OL(XW,207,XW,950)
S.wall(XW,207.0,150.5,213.0); S.OL(XW,207,150.5,207); S.OL(XW,213,150.5,213)
S.dimline(PL,190,150.5,190); S.dimline(XW,198,150.5,198,size=3.4)
S.small("PLOT LINE 7'-0\" FROM HOUSE (SURVEY PLAN); NEW 10'-0\" HIGH WALL 9\" THICK INSIDE IT",300,203,2.4)
# ---- servant quarters at grade (existing room top-left) ----
S.rect(XW+2,215,148.5,398,BLACK,0.48,dashes="[3 2] 0")
S.wall(XW,320.0,150.5,325.3); S.OL(XW,320,150.5,320); S.OL(XW,325.3,150.5,325.3)
S.wall(XW,400.0,150.5,405.3); S.OL(XW,400,150.5,400); S.OL(XW,405.3,150.5,405.3)
S.wall(100.0,325.3,106.0,400.0); S.OL(100,325.3,100,400); S.OL(106,325.3,106,400)
S.rect(58,222,96,300,FURN,0.48); S.line(58,242,96,242,FURN,0.48)
S.rect(104,222,142,300,FURN,0.48); S.line(104,242,142,242,FURN,0.48)
S.text("SERVANT ROOM",101,256,4.6); S.text(dimstr(XW,213,150.5,320),101,261,3.6); S.small("EXISTING, AT GRADE (+0)",101,266,2.6); S.small("ROOM 2 ABOVE AT +9'-0\"",101,271,2.6)
toilet_symbols(S, wc=(90,74,350), basin=(90,74,386)); S.text("RESTROOM",76,368,3.4); S.small(dimstr(XW,325.3,100,400),76,373,2.6)
S.door(100,340,106,370,'y0','right')                                     # restroom from room? no: from entry
S.door(110,320.0,145,325.3,'x0','up')                                    # entry -> room
S.door(110,400.0,145,405.3,'x0','up')                                    # yard -> entry
S.text("ENTRY",128,356,3.6); S.small(dimstr(106,325.3,150.5,400),128,361,2.6); S.small("HE ENTERS HERE",128,366,2.4)
S.small("SERVANT QUARTERS, ENTRY FROM OUTSIDE ONLY",101,395,2.6)
# ---- yard north of the block: one open garden court at grade, tiered planters against the house, path along the wall ----
S.rect(XW+2,407,148.5,681,BLACK,0.48,dashes="[3 2] 0")
for gx in range(XW+6 if False else 58,148,8):
    for gy in range(412,678,8): S.line(gx,gy,gx+1,gy+1,FURN,0.3)
S.line(90,405.3,90,683.6,FURN,0.48,dashes="[1 3] 0"); S.small("PATH 2'-4\"",72,545,2.4); S.small("ALONG WALL",72,550,2.4)
# bath deck at +60" outside the bathroom with the outdoor shower (full-height glazing)
S.rect(118,410,150.5,478,FURN,0.72); toilet_symbols(S, shower=(0,132,438)); S.small("BATH DECK +60\"",134,486,2.4); S.small("OUTDOOR SHOWER",134,491,2.4)
# steps down from the dressing to the garden (9 risers), landing at the sliding door
S.rect(103,611.7,150.5,664,MAG,0); S.stair(103,548,150.5,611.7,9,'up'); S.text("DN 9 R",126,540,3.6,color=MAG)
S.sliding(150.5,611.7,170.0,663.9)
for i,yy in enumerate((495,515,535)): S.rect(96,yy,116,yy+14,FURN,0.48)
for yy in (670,676,682): S.line(96,yy,150.5,yy,FURN,0.48)
S.circle(118,655,10,FURN,0.48); S.circle(118,655,6,FURN,0.24)
S.text("GARDEN",70,620,4.6); S.text("COURT",70,626,4.6); S.small(dimstr(XW,405.3,150.5,683.6),70,631,2.8); S.small("AT GRADE, TIERED PLANTERS",70,636,2.4); S.small("FROM DRESSING BY STEPS",70,641,2.4)
# external stair to room 2 over the servant block, along the boundary wall
S.stair(XW,405.3,88,500,11,'up'); S.text("UP TO",70,508,3.4,color=MAG); S.text("ROOM 2",70,513,3.4,color=MAG)
columns(S); S.small("EXTERNAL COLUMNS TO TERRACE",360,942,2.8)
# porch: existing light well kept as planted sunken court (no stair); entrance landing + straight steps
S.rect(190.0,683.6,513.0,754.0,BLACK,0.48,dashes="[3 2] 0")
S.stair(395.0,704.0,513.0,750.0,10,'left'); S.rect(345.0,704.0,395.0,750.0,MAG,0); S.rect(345.0,683.6,391.0,689.0,BLACK,0.48,dashes="[2 1] 0")
S.text("DN",454,748,5.0,color=MAG); S.small("11 R TO BASEMENT, LANDING AT DOOR BELOW",454,754,2.6,color=MAG)
S.circle(240,720,14,FURN,0.48); S.circle(240,720,9,FURN,0.24); S.text("SUNKEN GARDEN COURT",268,760,5.0); S.text(dimstr(190,683.6,513,754),268,772,3.6); S.small("EXISTING LIGHT WELL, PLANTED (NORTH-EAST KEPT OPEN); EXTENDED WEST FOR THE STAIR",268,766,2.6)
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
# entrance steps: compact flight directly outside the existing door, north pada 5, outside the Brahmasthan
S.rect(560,683.6,717,745,MAG,0); S.stair(560,745,717,810,6,'up'); S.text("UP 6 R",638,818,4.6,color=MAG)
S.rect(520,683.6,556,810,FURN,0.48); S.rect(721,683.6,757,810,FURN,0.48)
for yy in range(690,805,24): S.circle(538,yy+10,8,FURN,0.24); S.circle(739,yy+10,8,FURN,0.24)
S.text("GRAND ENTRANCE",638,828,5.0); S.text("LANDING "+dimstr(560,683.6,717,745)+", FLIGHT "+dimstr(560,745,717,810),638,838,3.4); S.small("10'-0\" WIDE FLIGHT + LANDING, PLANTERS BOTH SIDES, DOUBLE-HEIGHT PORTE-COCHERE UNDER THE NEW NORTH WING",638,833,2.6)
S.small("ENTRANCE DOOR WIDENED TO 6'-0\" DOUBLE DOOR (NEW LINTEL)",625,678,2.4)
# notes
ny=990
for t in ["NOTES (REVISION R3):",
          "A. EAST PLOT LINE 7'-0\" FROM THE HOUSE (SURVEY PLAN, TOP-LEFT CORNER), TAKEN STRAIGHT FOR THE FULL LENGTH. NEW 10'-0\" HIGH BOUNDARY WALL 9\" THICK INSIDE IT: CLEAR STRIP 6'-3\". NO OPENINGS TO THE PARK EXCEPT THE EVENT GATE; CAR GATE 10'-0\" AT THE EAST END OF THE NORTH BOUNDARY.",
          "B. CONCEALED EVENT GATE IN THE EAST BOUNDARY WALL FROM THE HOUSE CORNER TO THE FRONT BOUNDARY: FLUSH WALL-FINISHED PANELS ON CONCEALED PIVOTS, OPENED ONLY FOR EVENTS.",
          "C. COURTYARD-01 IN THE EXISTING STAIRWELL SHAFT, OPEN TO SKY THROUGH ALL FLOORS: THE BRAHMASTHAN (CENTRE OF THE WHOLE-HOUSE GRID) IS KEPT OPEN AND FREE OF STAIRS. ENTRANCE STEPS ARE A COMPACT 6-RISER FLIGHT OUTSIDE THE EXISTING DOOR; BASEMENT STAIR IN THE WEST PART OF THE EXISTING LIGHT WELL. LIFT GIVES THE STEP-FREE ROUTE.",
          "D. EAST STRIP: SERVANT QUARTERS AT GRADE IN THE SOUTH-EAST (EXISTING ROOM; RESTROOM ON THE EAST, ENTRY ON THE WEST; SECOND ROOM ABOVE AT +9'-0\" BY AN EXTERNAL STAIR ALONG THE WALL), ENTERED FROM OUTSIDE ONLY, NO DOOR INTO THE HOUSE. NORTH OF IT ONE OPEN GARDEN COURT AT GRADE WITH TIERED PLANTERS, THE SERVANT'S PATH ALONG THE WALL, A BATH DECK AT +60\" WITH THE OUTDOOR SHOWER, AND STEPS DOWN FROM THE DRESSING.",
          "E. SERVICE WING ROOFED AT 7'-6\" WITH A PLANTER PARAPET; BATHROOM EAST WINDOW IN OBSCURE GLASS. GRAND ENTRANCE: 10'-0\" FLIGHT CENTRED ON THE WIDENED FRONT DOOR (NORTH PADA 5), BELOW THE BRAHMASTHAN LINE. BASEMENT STAIR IN THE NORTH LIGHT WELL. THE WHOLE BLOCK OVER THE PORCH (LOBBY, LIFT, MAIN STAIR, UPPER LIVING ROOMS) IS DEMOLISHED AND REBUILT ON THE NEW COLUMN GRID; LIFT AND MAIN STAIR STAY IN THE NORTH-WEST.",
          "F. ALL ROOM DIMENSIONS ARE CLEAR INTERNAL SIZES TAKEN FROM THE DRAWN WALLS. SHEET ORIENTATION: TOP = SOUTH, BOTTOM = NORTH, LEFT = EAST, RIGHT = WEST."]:
    S.note(t,150.5,ny,5.0); ny+=8
S.commit()

# ================= FIRST FLOOR (page 1) =================
ff=doc[1]
DELF=[TR(r,T_FF) for r in [(166,505,428,718),(575,512,744,667),(930,505,1057,664),(556,762,571,800)]]
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
# north-east wing over porch
columns(F)
ne_wing(F,728.1,935.8,"BEDROOM-03",'4\'-9" X 8\'-10"','6\'-9" X 12\'-5"','12\'-1" X 12\'-5"',779)
F.wall(557.3,728.1,569.1,733); F.door(557.3,733,569.1,779,'y0','right'); F.wall(557.3,779,569.1,785)
F.door(170,720.2,212,728.1,'x0','down')                                              # study -> garden (in existing window opening)
for gx0,gx1 in ((344.7,399.6),(438.8,516.8)):
    F.wall(gx0,720.2,gx1,728.1); F.OL(gx0,720.2,gx1,720.2); F.OL(gx0,728.1,gx1,728.1)   # former windows now internal: infilled
ny=1000
for t in ["NOTES (FIRST FLOOR, R3):","1. THE BLOCK OVER THE PORCH IS REBUILT FROM SCRATCH ON RCC COLUMNS FROM FOUNDATION TO TERRACE (THREE ON THE PORCH LINE, THREE AT THE BACK AGAINST THE NORTH WALL, NONE WITHIN THE 10'-0\" CAR GATE OR THE DRIVE LINE), INDEPENDENT OF THE STONE WALLS; TO STRUCTURAL DESIGN.",
          "2. FORMER WEST TERRACE ENCLOSED AS MASTER WALK-IN CLOSET (LIGHT PARTITIONS ON EXISTING SLAB). 3. NORTH-EAST ROOM RE-PURPOSED AS STUDY WITH PUJA IN ITS NORTH-EAST CORNER.",
          "4. COURTYARD VOID WITHIN THE EXISTING STAIRWELL SHAFT; GLASS BALUSTRADE. 5. ROOM DIMENSIONS ARE CLEAR INTERNAL SIZES FROM THE DRAWN WALLS."]:
    F.note(t,150.1,ny,5.0); ny+=8
F.commit()

# ================= SECOND FLOOR (page 2) =================
sf=doc[2]
DELS=[TR(r,T_SF) for r in [(104,225,256,396),(266,225,431,396),(165,406,431,745),(447,509,561,751),(447,225,721,493),(575,512,744,667),(556,762,571,812),(214,278,266,336),(398,390,450,470),(572,700,816,932),(257,222,265,296),(257,341,265,399),(95,397.5,345.5,405),(401,397.5,445.5,405),(432.5,403.5,445.5,441)]]
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
ny=1000
for t in ["NOTES (SECOND FLOOR, R3):","1. SOUTH-EAST TOILET, WALK-IN CLOSET AND BEDROOM-02 REMOVED; THE SOUTH-EAST CORNER WITH THE BEST VIEW BECOMES THE LIVING ROOM, THE REST A COMMON LOUNGE. FORMER NORTH WINDOWS BECOME DOORS TO THE GARDEN AND BEDROOM-02, OR ARE INFILLED.",
          "2. BEDROOM-02 WITH EN-SUITE IN THE FORMER LIVING OVER THE PORCH (NORTH-WEST); THE NEW EAST WING AT THIS LEVEL IS AN OPEN VIEW DECK ON EXTERNAL COLUMNS, NO WALLS. 3. STRUCTURAL WALL LINES RETAINED AS PIERS; OPENINGS WITH LINTELS.",
          "4. FAMILY GALLERY ALONG THE COURTYARD VOID. 5. ROOM DIMENSIONS ARE CLEAR INTERNAL SIZES FROM THE DRAWN WALLS."]:
    G.note(t,150.4,ny,5.0); ny+=8
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
Tt.wall(830,763.3,1084.6,775); Tt.wall(830,763.3,842,947.3); Tt.wall(892.7,775,904.4,873); Tt.wall(998.5,775,1010.2,873); Tt.wall(892.7,861.2,1010.2,873)
Tt.rect(904.4,775,998.5,861.2,FURN,0.48); Tt.line(904.4,775,998.5,861.2,FURN,0.24); Tt.line(904.4,861.2,998.5,775,FURN,0.24); Tt.text("LIFT",951,822,5.0)
Tt.stair(1015,780,1070,935,12,'up'); Tt.text("DN",1042,945,5.0,color=MAG)
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
ny=1000
for t in ["NOTES (TERRACE, R5):","1. PARAPET 3'-6\" HIGH ALL ROUND; COURTYARD VOID RAILED. 2. WATER TANKS, CENTRAL WATER HEATER, AC OUTDOOR UNITS AND PUMPS IN A LOUVRED SERVICES ENCLOSURE IN THE SOUTH-WEST; SOLAR PV ALONG THE SOUTH PARAPET; NORTH-EAST KEPT OPEN AND LOW (VASTU).",
          "3. SKY PAVILION ON THE EAST: STEEL FRAME, RETRACTABLE LOUVRE ROOF, SLIDING GLASS WITH INSECT SCREENS, BAR, DINING AND LOUNGE; POWER AND WATER TO THE BAR. 4. STAFF ROOM, WC, GUEST WC AND SCREENED DRYING YARD BESIDE THE MUMTY (NORTH-WEST).",
          "5. TERRACE SLAB OVER THE NORTH WING CARRIED ON THE EXTERNAL COLUMNS (DASHED); PAVILION AND SERVICES LOADS TO BE CHECKED BY THE STRUCTURAL ENGINEER. 6. WATERPROOFING AND SLOPES TO NORTH-EAST DRAIN POINTS."]:
    Tt.note(t,150.1,ny,5.0); ny+=8
Tt.commit()

# order: BF, GF, FF, SF, TF
doc.move_page(3,0)   # basement to front
doc.save(OUT,garbage=1,deflate=True); print("saved",OUT,len(doc))
