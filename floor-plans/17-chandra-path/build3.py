import pymupdf
from csedit import edit_page
from plan import *
SRC="proposed.pdf"; OUT="Proposed_Floor_Plan-20260916-R4.pdf"
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
    S.label(bedname,bdim,373,y0+150,7.0)
    # toilet
    toilet_symbols(S, wc=(180,513,yi-20), basin=(-90,513,corr_y1+22), shower=(0,500,corr_y1+60))
    S.line(476,corr_y1+40,551,corr_y1+40,FURN,0.48,dashes="[2 2] 0")
    S.text("TOILET",513,corr_y1+80,5.0); S.text(tdim,513,corr_y1+86,4.0)
    # garden
    S.circle(216,y0+95,15,FURN,0.48); S.circle(216,y0+95,10,FURN,0.24)
    for pts in ([(180,y0+40),(194,y0+37),(199,y0+48),(186,y0+52)],[(240,y0+150),(252,y0+147),(256,y0+158),(244,y0+162)]): S.poly(pts,FURN,0.48)
    S.text("N-E GARDEN",216,y0+30,5.0); S.text(gdim,216,y0+36,4.0); S.small("OPEN TERRACE, PLANTED",216,y0+42,3.0)
    S.text("CORRIDOR",513,y0+22,4.0)

# ================= GROUND FLOOR =================
gf=doc[0]
DEL=[R_(*r) for r in [
    (170.5,230.3,421.0,352.3),(170.5,352.3,394.0,402.3),(170.5,501.0,340.0,663.5),(340.0,546.0,394.0,663.5),
    (394.0,511.5,561.0,664.2),(437.0,492.5,484.7,512.0),(439.0,496.0,482.5,539.0),(150.3,611.5,170.2,664.1),
    (70.0,378.0,148.0,404.0),(45.0,468.0,150.4,473.0),
    (582.0,513.0,746.5,636.0),(655.0,636.0,746.5,667.5),          # foyer contents -> courtyard
]]
print("GF:",edit_page(doc,gf,DEL,KEEP=[R_(402.1,511.8,437.4,511.8)]))
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
S.label("KITCHEN",'15\'-11" X 11\'-0"',300.0,378.0); S.small("BREAKFAST ISLAND",297,325,3.2)
S.line(232.0,410.7,232.0,492.9,FURN,0.48,dashes="[2 2] 0")
S.wall(296.0,560.0,303.9,663.9); S.OL(296,560,296,663.9); S.OL(303.9,560,303.9,663.9); S.OL(296,560,303.9,560)
S.hatch(170.0,500.7,252.0,527.0); S.hatch(270.0,560.0,296.0,663.9); S.rect(170.0,545.0,190.0,605.0); S.circle(200,575,6)
S.sliding(150.5,611.7,170.0,663.9); S.label("DRESSING",'8\'-0" X 10\'-4"',236.0,600.0)
bed(S,418,511.8,side=False); S.rect(396,511.8,416,531.8); S.rect(520,511.8,540,531.8)
S.rect(312,560,342,590); S.circle(357,575,8); S.rect(445,634,515,656); S.circle(480,624,6); S.rect(330,650,430,662)
S.label("BEDROOM-01",'16\'-5" X 10\'-6"',362.0,618.0)
# east side yard: straightened wall at x=80, service wing along the full east side
XW=80.0
S.line(XW,210.9,XW,940,GREY,1.2,dashes="[4 2] 0")
for y in (282.0,400.0,478.0,555.0): S.wall(XW,y,150.5,y+5.3); S.OL(XW,y,150.5,y); S.OL(XW,y+5.3,150.5,y+5.3)
S.wall(XW,214.0,150.5,219.3); S.OL(XW,214,150.5,214); S.OL(XW,219.3,150.5,219.3)
S.door(105.0,282.0,140.0,287.3,'x1','up')                                    # staff toilet from utility
toilet_symbols(S, wc=(0,115,240), basin=(180,90,258))
S.text("STAFF",112,266,4.6); S.text("TOILET",112,272,4.6); S.text('4\'-6" X 4\'-4"',112,278,3.8)
# utility: WM + sink, door from kitchen cut below existing window (lintel retained)
S.door(150.5,300.0,170.0,340.0,'y0','left')
S.rect(84,292,110,318,FURN,0.48); S.circle(97,305,9); S.small("WM",97,326,3.0)
S.rect(84,330,110,360,FURN,0.48); S.rrect(88,334,106,356,2,PURPLE,0.24)
S.rect(84,364,110,396,FURN,0.48); S.small("SHELVES",97,392,2.6)
S.text("UTILITY",125,346,4.6); S.text('4\'-6" X 7\'-2"',125,352,3.8)
toilet_symbols(S, shower=(0,100,438))
S.text("BATH",128,428,4.6); S.text("COURT",128,434,4.6); S.small("OUTDOOR SHOWER",128,440,3.0); S.small("PLANTED, OPEN",128,445,2.8); S.small("FULL HT. GLAZING",132,468,2.8)
S.hatch(84,488,150.5,500); S.hatch(84,540,150.5,552); S.text("STORE",115,522,4.6); S.text('4\'-6" X 4\'-7"',115,528,3.8)
S.circle(105,655,14,FURN,0.48); S.circle(105,655,9,FURN,0.24)
for yy in (566,582,598,614): S.rect(84,yy,100,yy+12,FURN,0.48)
S.small("PLANTERS",92,634,2.6)
for pts in ([(118,575),(134,572),(140,584),(126,590)],[(126,610),(138,606),(142,616),(130,620)]): S.poly(pts,FURN,0.48)
S.text("GREEN",128,596,4.6); S.text("COURT",128,602,4.6); S.small("SEEN FROM DRESSING",128,608,2.8)
S.line(XW,214,XW,683.6,FURN,0.48,dashes="[1 2] 0"); S.small("ROOF PLANTERS OVER SERVICE WING",115,208,2.8)
# porch: sunken court + basement stair
S.rect(190.0,683.6,395.0,754.0,BLACK,0.48,dashes="[3 2] 0"); S.stair(200.0,692.0,331.0,742.0,10,'right'); S.rect(331.0,692.0,395.0,742.0,MAG,0)
S.rect(345.0,683.6,391.0,689.0,BLACK,0.48,dashes="[2 1] 0"); S.text("DN",265,748,5.0,color=MAG); S.text("SUNKEN GARDEN COURT",292,764,5.0); S.text("(BASEMENT ENTRY BELOW)",292,770,4.2)
# concealed event gate on east boundary (porch length)
S.line(XW,683.6,XW,940,RED,1.6,dashes="[6 3] 0")
S.text("CONCEALED EVENT GATE",130,905,4.6,color=RED); S.text("FLUSH WALL PANELS",130,911,3.8,color=RED)
# pergola in west garden
x0,y0,x1,y1=1026,245,1102,382; S.rect(x0,y0,x1,y1,FURN,0.48); x=x0+5
while x<x1: S.line(x,y0,x,y1,FURN,0.24); x+=5
S.text("PERGOLA",1064,395,5.0); S.text("LOUNGE",1064,401,5.0)
# courtyard-01 in foyer
S.rect(655,512,743,655,FURN,0.48); S.rect(658,515,740,652,FURN,0.24)
S.circle(699,583,22,FURN,0.48); S.circle(699,583,15,FURN,0.24); S.circle(699,583,3,FURN,0.48)
for gx in range(662,740,9):
    for gy in range(519,652,9): S.line(gx,gy,gx+1,gy+1,FURN,0.3)
S.text("COURTYARD-01",699,630,6.0); S.text('5\'-7" X 9\'-1"',699,637,4.6); S.small("OPEN TO SKY THROUGH ALL FLOORS",699,643,3.0); S.small("TREE IN 3'-0\" DEEP PLANTER, WATERPROOFED",699,648,3.0)
S.text("ENTRANCE",612,585,5.0); S.text("FOYER",612,591,5.0); S.text('5\'-6" WIDE',612,597,4.0)
# notes
ny=990
for t in ["NOTES (REVISION R3):",
          "A. EAST BOUNDARY WALL TO BE REBUILT STRAIGHT AND PARALLEL TO THE HOUSE (SHOWN DASHED AT THE WIDEST OFFSET); SIDE COURTS SET OUT FROM THE NEW WALL.",
          "B. CONCEALED EVENT GATE IN THE EAST BOUNDARY WALL FROM THE HOUSE CORNER TO THE FRONT BOUNDARY: FLUSH WALL-FINISHED PANELS ON CONCEALED PIVOTS, OPENED ONLY FOR EVENTS.",
          "C. COURTYARD-01: OPEN TO SKY THROUGH FIRST, SECOND AND TERRACE FLOORS WITHIN THE EXISTING STAIRWELL SHAFT; NO NEW SLAB OPENINGS. GLASS BALUSTRADE AT EACH FLOOR.",
          "D. SERVICE WING ALONG THE FULL EAST SIDE (STAFF TOILET, UTILITY, BATH COURT, STORE, GREEN COURT), 4'-6\" WIDE FROM THE STRAIGHTENED WALL; KITCHEN-UTILITY DOOR CUT BELOW THE EXISTING WINDOW, LINTEL RETAINED.",
          "E. SERVICE WING ROOF AT 7'-6\" WITH A CONTINUOUS PLANTER PARAPET (GREEN VIEW FROM KITCHEN, BATH AND DRESSING TOWARDS THE PARK SIDE). STAFF ROOM ON THE TERRACE FLOOR BESIDE THE MUMTY (SEE TF-PP-01).",
          "F. VASTU GRID (RED) IS AN ASSESSMENT OVERLAY ONLY. SHEET ORIENTATION: TOP = SOUTH, BOTTOM = NORTH, LEFT = EAST, RIGHT = WEST."]:
    S.note(t,150.5,ny,5.0); ny+=8
vastu_grid(S,150.5,210.9,1099,683.6)
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
F.text("PUJA",210,680,5.0); F.text('5\'-7" X 4\'-8"',210,686,4.0)
F.rect(300,560,362,592); F.circle(331,604,6); F.hatch(270,700,425,720.2)           # desk, chair, book wall
F.rrect(180,540,240,570,4); F.circle(258,555,8)                                       # cosy sofa + table
F.rect(380,510,425,528,FURN,0.48); F.small("MEMENTO SHELVES",402,536,2.8)
F.label("STUDY / MEMENTO ROOM",'17\'-0" X 13\'-10½"',300.0,640.0)
F.small("VIDEO-CALL WALL: EAST FACING",300,660,3.0)
# master walk-in closet in former west terrace
F.hatch(930,505,1057,528); F.hatch(930,644,1057,667); F.rect(972,570,1015,600); F.small("ISLAND",993,606,2.8)
F.door(920.7,560,928.5,600,'y0','left')                                             # closet -> bathroom
F.label("WALK-IN CLOSET",'8\'-3" X 10\'-5"',993.0,588.0,7.0)
# north-east wing over porch
ne_wing(F,728.1,935.8,"BEDROOM-03",'4\'-9" X 8\'-10"','6\'-9" X 12\'-5"','12\'-1" X 12\'-5"',779)
F.wall(557.3,728.1,569.1,733); F.door(557.3,733,569.1,779,'y0','right'); F.wall(557.3,779,569.1,785)
F.door(200,720.2,240,728.1,'x0','down')                                              # study -> garden
ny=1000
for t in ["NOTES (FIRST FLOOR, R3):","1. NEW SLAB OVER THE PORCH EXTENDED EAST TO THE HOUSE LINE; SUPPORTED ON THE EXISTING NORTH WALL AND NEW COLUMNS ON THE PORCH LINE, TO STRUCTURAL DESIGN.",
          "2. FORMER WEST TERRACE ENCLOSED AS MASTER WALK-IN CLOSET (LIGHT PARTITIONS ON EXISTING SLAB). 3. NORTH-EAST ROOM RE-PURPOSED AS STUDY WITH PUJA IN ITS NORTH-EAST CORNER.",
          "4. COURTYARD VOID WITHIN THE EXISTING STAIRWELL SHAFT; GLASS BALUSTRADE. 5. VASTU GRID (RED) IS AN ASSESSMENT OVERLAY ONLY."]:
    F.note(t,150.1,ny,5.0); ny+=8
vastu_grid(F,150.1,210.9,1084.6,935.8)
F.commit()

# ================= SECOND FLOOR (page 2) =================
sf=doc[2]
DELS=[TR(r,T_SF) for r in [(104,225,256,396),(266,225,431,396),(165,406,431,745),(447,509,561,751),(447,225,721,493),(575,512,744,667),(556,762,571,812),(214,278,266,336),(398,390,450,470),(257,222,265,296),(257,341,265,399),(95,397.5,345.5,405),(401,397.5,445.5,405),(432.5,403.5,445.5,441)]]
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
G.label("SEMI-OPEN LOUNGE",'34\'-0" X 21\'-0" (L-SHAPED)',300.0,660.0)
G.text("VIEW VERANDAH",180,300,5.0); G.text("SEMI-OPEN, BEST VIEW",180,306,3.6); G.small("SLIDING GLASS + SCREENS",180,311,2.8)
G.small("EXISTING PIER LINE RETAINED, WIDE OPENING WITH LINTEL",438,470,2.6)
G.text("LUGGAGE /",504,620,5.0); G.text("STORE",504,626,5.0)
ne_wing(G,759.4,935.6,"BEDROOM-02",'4\'-9" X 7\'-6"','6\'-9" X 10\'-6"','12\'-1" X 10\'-6"',810)
G.wall(557.5,690.8,569.2,765); G.door(557.5,765,569.2,811,'y0','right'); G.wall(557.5,811,569.2,816)
ny=1000
for t in ["NOTES (SECOND FLOOR, R3):","1. SOUTH-EAST TOILET, WALK-IN CLOSET AND BEDROOM-02 REMOVED; AREA BECOMES A SEMI-OPEN LOUNGE WITH THE VIEW VERANDAH AT THE SOUTH-EAST.",
          "2. BEDROOM-02 AND ITS TOILET RELOCATED TO THE NEW NORTH WING OVER THE PORCH (NORTH ZONE). 3. STRUCTURAL WALL LINES RETAINED AS PIERS; OPENINGS WITH LINTELS.",
          "4. FAMILY GALLERY ALONG THE COURTYARD VOID. 5. VASTU GRID (RED) IS AN ASSESSMENT OVERLAY ONLY."]:
    G.note(t,150.4,ny,5.0); ny+=8
vastu_grid(G,150.4,210.9,1084.6,935.6)
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
vastu_grid(B,150.5,210.9,1099,683.6)
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
Tt.rect(726,840,768,924,FURN,0.48); Tt.line(726,858,768,858,FURN,0.48); Tt.text("STAFF ROOM",800,880,5.0); Tt.text('7\'-0" X 7\'-0"',800,886,4.0)
Tt.rect(600,800,708,941.3,FURN,0.48,dashes="[2 2] 0"); Tt.text("CLOTHES DRYING",654,860,4.6); Tt.small("(SCREENED, NORTH-WEST)",654,866,2.8)
courtyard_void(Tt,label=False); Tt.text("COURTYARD VOID",699,578,6.0); Tt.text("SKYLIGHT OPENING",699,585,4.6); Tt.small("SAFETY RAILING 3'-6\" HIGH",699,591,3.0)
# zones
Tt.rect(1000,232,1075,300,FURN,0.48); Tt.line(1000,232,1075,300,FURN,0.24); Tt.text("WATER TANKS",1037,312,4.6); Tt.small("(SOUTH-WEST, HEAVY)",1037,317,2.8)
for i in range(10): Tt.rect(470+i*50,236,514+i*50,296,FURN,0.48)
Tt.text("SOLAR PANELS ON SOUTH EDGE",720,306,4.6)
x0,y0,x1,y1=180,400,430,640; Tt.rect(x0,y0,x1,y1,FURN,0.48); x=x0+5
while x<x1: Tt.line(x,y0,x,y1,FURN,0.24); x+=5
Tt.rrect(200,560,330,592,4); Tt.rrect(200,600,232,632,4); Tt.circle(290,615,18)
Tt.text("PERGOLA SKY LOUNGE",305,520,6.0); Tt.text('16\'-0" X 15\'-3"',305,527,4.6)
Tt.rect(180,240,300,270,FURN,0.48); Tt.text("BAR / PANTRY",240,282,4.6); Tt.small("(SOUTH-EAST)",240,287,2.8)
Tt.rect(X0+6,Y1-40,830,Y1-6,FURN,0.48,dashes="[2 2] 0"); Tt.text("PLANTER STRIP ALONG NORTH EDGE",480,Y1-20,4.6)
Tt.rect(X0+6,Y0+6,300,240,FURN,0.48,dashes="[2 2] 0")
Tt.text("OPEN TERRACE",620,470,8.0); Tt.text("FAMILY / EVENT SPACE, NORTH-EAST KEPT OPEN AND LOW",620,479,4.6)
ny=1000
for t in ["NOTES (TERRACE, R3):","1. PARAPET 3'-6\" HIGH ALL ROUND; COURTYARD VOID RAILED. 2. WATER TANKS AND PLANT IN THE SOUTH-WEST; SOLAR ARRAY ALONG THE SOUTH PARAPET; NORTH-EAST KEPT OPEN AND LOW (VASTU).",
          "3. PERGOLA LOUNGE ON THE EAST; BAR AT THE SOUTH-EAST. 4. STAFF ROOM, WC AND SCREENED DRYING YARD BESIDE THE MUMTY (NORTH-WEST). 5. WATERPROOFING AND SLOPES TO NORTH-EAST DRAIN POINTS. 6. VASTU GRID (RED) IS AN ASSESSMENT OVERLAY ONLY."]:
    Tt.note(t,150.1,ny,5.0); ny+=8
vastu_grid(Tt,150.1,210.9,1084.6,947.3)
Tt.commit()

# order: BF, GF, FF, SF, TF
doc.move_page(3,0)   # basement to front
doc.save(OUT,garbage=1,deflate=True); print("saved",OUT,len(doc))
