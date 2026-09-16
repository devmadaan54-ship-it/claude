import pymupdf, sys
from csedit import edit_page
from plan import *
SRC="proposed.pdf"; OUT="Proposed_Floor_Plan-20260916-R2.pdf"
doc=pymupdf.open(SRC); orig=pymupdf.open(SRC)
R_=pymupdf.Rect

# ================= GROUND FLOOR (page 0) =================
gf=doc[0]
DEL=[R_(*r) for r in [
    (170.5,230.3,421.0,352.3),(170.5,352.3,394.0,402.3),          # bedroom-01 interior -> kitchen
    (170.5,501.0,340.0,663.5),(340.0,546.0,394.0,663.5),          # bedroom-02 interior
    (394.0,511.5,561.0,664.2),(437.0,492.5,484.7,512.0),(439.0,496.0,482.5,539.0),   # kitchen interior, partition, door
    (150.3,611.5,170.2,664.1),                                    # bedroom east window -> sliding glass door
    (70.0,378.0,148.0,404.0),(45.0,468.0,150.4,473.0),            # exterior toilet label + its boundary line
]]
KEEP=[R_(402.1,511.8,437.4,511.8)]
print("GF edits:",edit_page(doc,gf,DEL,KEEP=KEEP))
S=Sheet(gf,orig[0])
# --- walls ---
S.wall(437.4,492.9,484.3,511.8); S.OL(437.4,492.9,484.3,492.9); S.OL(437.4,511.8,484.3,511.8)
S.OL(394.3,511.8,402.1,511.8); S.OL(394.3,663.9,402.1,663.9)
# --- KITCHEN (south-east room) ---
CD=31.6
S.rect(170.0,230.4,201.6,402.8); S.rect(201.6,230.4,420.4,230.4+CD)
hx0,hy0=172.5,238.0; S.rect(hx0,hy0,hx0+26.5,hy0+34.0)
for dx,dy in ((7.5,8.5),(19,8.5),(7.5,25.5),(19,25.5)): S.circle(hx0+dx,hy0+dy,4.0)
sx0,sy0=174.0,362.0; S.rrect(sx0,sy0,sx0+24,sy0+34,3,PURPLE,0.24); S.rrect(sx0+3,sy0+3,sx0+21,sy0+31,2,PURPLE,0.24); S.circle(sx0+21.5,sy0+17,1.6,PURPLE,0.24)
S.rect(384.4,262.0,420.4,298.0); S.line(384.4,280,420.4,280,FURN,0.48); S.line(414.4,262,414.4,298,FURN,0.48)
S.rect(250.0,300.0,344.0,347.0); S.line(250,300,344,347,FURN,0.24); S.line(250,347,344,300,FURN,0.24)   # island
for cy in (312,335): S.circle(353,cy,5.5)
S.label("KITCHEN",'15\'-11" X 11\'-0"',300.0,378.0); S.small("BREAKFAST ISLAND",297,325,3.2)
# --- BATHROOM (existing, east side): glass screen + full height glazing to bath court ---
S.line(232.0,410.7,232.0,492.9,FURN,0.48,dashes="[2 2] 0")
# --- BEDROOM SUITE: dressing at east end, bedroom with bed head on SOUTH wall ---
S.wall(296.0,560.0,303.9,663.9); S.OL(296,560,296,663.9); S.OL(303.9,560,303.9,663.9); S.OL(296,560,303.9,560)
S.hatch(170.0,500.7,252.0,527.0)                     # wardrobe A (south wall of dressing)
S.hatch(270.0,560.0,296.0,663.9)                     # wardrobe B (against partition)
S.rect(170.0,545.0,190.0,605.0); S.circle(200,575,6)  # dressing table + stool
S.sliding(150.5,611.7,170.0,663.9)                   # glass door to private garden court
S.label("DRESSING",'8\'-0" X 10\'-4"',236.0,600.0)
S.replay(lambda it: R_(229,230.3,335,366).contains(it["drect"]) and it["type"]!="f", pymupdf.Matrix(1,0,0,1,186.0,281.4))  # bed + rug
S.rect(396,511.8,416,531.8); S.rect(520,511.8,540,531.8)   # side tables
S.rect(312,560,342,590); S.circle(357,575,8)               # lounge chair + table
S.rect(445,634,515,656); S.circle(480,624,6)               # writing desk by window + chair
S.rect(330,650,430,662)                                    # TV console
S.label("BEDROOM-01",'16\'-5" X 10\'-6"',362.0,618.0)
# --- EAST SIDE YARD: staff toilet, herb court, bath court, private garden court ---
xb=lambda y: 41+0.053*(y-210)
S.wall(xb(282)+3,282.0,150.5,287.3); S.wall(xb(400)+3,400.0,150.5,405.3); S.wall(xb(478)+3,478.0,150.5,483.3)
for y in (282.0,287.3,400.0,405.3,478.0,483.3): S.OL(xb(y)+3,y,150.5,y)
S.door(105.0,282.0,140.0,287.3,'x1','up')
S.replay(lambda it: R_(240,411.2,300,458).contains(it["drect"]) and purple(it), pymupdf.Matrix(1,0,0,1,-150,-190))   # WC in staff toilet
S.replay(lambda it: R_(298,411.2,331,470).contains(it["drect"]) and purple(it), rot(316,452,180,72,258))              # basin
S.text("STAFF",100,240,5.0); S.text("TOILET",100,246,5.0); S.text('6\'-0" X 4\'-6"',100,252,4.2)
S.text("HERB",100,336,5.0); S.text("COURT",100,342,5.0)
S.replay(lambda it: R_(170.5,455,235,501).contains(it["drect"]) and purple(it), pymupdf.Matrix(1,0,0,1,-118,-40))   # outdoor shower
S.text("BATH",118,428,5.0); S.text("COURT",118,434,5.0); S.small("OUTDOOR SHOWER",118,440,3.0); S.small("FULL HT. GLAZING",130,468,2.8)
S.circle(98,650,16,FURN,0.48); S.circle(98,650,11,FURN,0.24)                     # small tree
for pts in ([(112,515),(128,512),(134,524),(120,530)],[(70,590),(84,586),(90,598),(76,604)],[(120,560),(132,556),(136,566),(124,570)]): S.poly(pts,FURN,0.48)
S.rect(140,535,150.5,585,FURN,0.48)                                                # bench
S.text("PRIVATE",105,600,5.0); S.text("GARDEN",105,606,5.0); S.text("COURT",105,612,5.0); S.small("GRAVEL + BOULDERS",105,618,3.0)
# --- PORCH: sunken garden court with basement stair ---
S.rect(190.0,683.6,395.0,754.0,BLACK,0.48,dashes="[3 2] 0")
S.stair(200.0,692.0,331.0,742.0,10,'right')
S.rect(331.0,692.0,395.0,742.0,MAG,0)
S.rect(345.0,683.6,391.0,689.0,BLACK,0.48,dashes="[2 1] 0")   # glazed door below (basement)
S.text("DN",265,748,5.0,color=MAG); S.text("SUNKEN GARDEN COURT",292,764,5.0); S.text("(BASEMENT ENTRY BELOW)",292,770,4.2)
# --- WEST GARDEN: pergola over the architect's outdoor seating ---
x0,y0,x1,y1=1026,245,1102,382
S.rect(x0,y0,x1,y1,FURN,0.48)
x=x0+5
while x<x1: S.line(x,y0,x,y1,FURN,0.24); x+=5
S.text("PERGOLA",1064,395,5.0); S.text("LOUNGE",1064,401,5.0)
S.commit()

# ================= BASEMENT (new page 0, copied from GF) =================
doc.fullcopy_page(0); doc.move_page(len(doc)-1,0)
bf=doc[0]
PLAN=[R_(34,26,1640,1166)]
TXT=[R_(34,26,1640,1166), R_(1390,630,1600,675), R_(1396,828,1470,846)]   # plan text + sheet title + drawing no
print("BF edits:",edit_page(doc,bf,PLAN,TEXTDEL=TXT))
B=Sheet(bf,orig[0])
B.text("BASEMENT -",1392.8,648.0,17.09,align="left",fontpath=ARIALB)
B.text("RENOVATION LAYOUT",1392.4,668.5,17.09,align="left",fontpath=ARIALB)
B.text("BF-PP-01",1398.1,840.5,14.12,align="left",fontpath=ARIAL)
# outline: outer faces as GF, walls 25pt (1'-7")
E,Wt,So,No=150.5,708.0,210.9,683.6   # outer faces
ei,wi,si,ni=176.0,683.0,236.0,658.0  # inner faces
B.wall(E,So,Wt,si); B.wall(E,So,ei,No); B.wall(wi,So,Wt,501.0); B.wall(E,ni,617.0,No)
# store (old stairwell) protrudes west of basement line under the foyer
B.wall(617.0,ni,768.0,No); B.wall(743.0,501.0,768.0,No); B.wall(617.0,501.0,768.0,509.0); B.wall(617.0,509.0,623.0,ni)
for a in [(E,si,Wt,si),(ei,So,ei,ni),(wi,si,wi,501),(ei,ni,617,ni),(617,ni,743,ni),(743,509,743,ni),(683,501,743,501)]: pass
# outlines on inner faces
B.OL(ei,si,wi,si); B.OL(ei,si,ei,ni); B.OL(wi,si,wi,501); B.OL(ei,ni,wi,ni); B.OL(623,509,743,509); B.OL(743,509,743,ni); B.OL(623,509,623,ni); B.OL(617,501,683,501); B.OL(617,509,617,ni)
B.OL(E,So,Wt,So); B.OL(E,So,E,No); B.OL(Wt,So,Wt,501); B.OL(Wt,501,768,501); B.OL(768,501,768,No); B.OL(E,No,768,No)
# columns + partition (theater / lounge)
B.wall(425.0,si,439.0,ni); B.OL(425,si,425,ni); B.OL(439,si,439,ni)
for cy in (375,485): B.rect(422,cy,442,cy+14,BLACK,0.72,GREY)
# north strip partitions: powder/gym/store
B.wall(439.0,501.0,617.0,507.0); B.OL(439,501,617,501); B.OL(439,507,617,507)
B.wall(566.0,507.0,572.0,ni); B.OL(566,507,566,ni); B.OL(572,507,572,ni)
# doors
B.door(425.0,420.0,439.0,467.0,'y0','right')     # theater
B.door(425.0,560.0,439.0,607.0,'y0','right')     # gym
B.door(566.0,520.0,572.0,560.0,'y0','right')     # shower/wc off gym
B.door(630.0,501.0,670.0,509.0,'x0','down')     # store from theater (AV / store)
# windows + glazed door to sunken court
B.window(E,536.0,ei,636.0)
B.window(195.0,ni,340.0,No)
B.door(345.0,ni,391.0,No,'x1','up')
B.small("GLAZED DOOR IN EXISTING",368,652,2.8); B.small("WINDOW OPENING, LINTEL RETAINED",368,656,2.8)
# sunken court + stair outside north wall
B.rect(190.0,No,395.0,754.0,BLACK,0.48,dashes="[3 2] 0")
B.stair(200.0,692.0,331.0,742.0,10,'left'); B.rect(331.0,692.0,395.0,742.0,MAG,0)
B.text("UP",265,748,5.0,color=MAG); B.text("SUNKEN GARDEN COURT",292,764,5.0); B.text("EXISTING LIGHT WELL, PLANTED",292,770,4.2)
B.line(120,No,1000,No,FURN,0.48,dashes="[4 2] 0"); B.text("PORCH ABOVE",560,700,5.0)
# --- LOUNGE + BAR (east half, by the windows) ---
B.rect(ei,si,262,262); B.rect(ei,262,202,330)                  # L bar counter
for cy in (275,300,322): B.circle(212,cy,5.5)
B.rect(262,si,420,262,FURN,0.48); B.small("WINE / DISPLAY WALL",341,251,3.0)
B.rrect(200,540,330,572,4); B.rrect(200,580,232,650,4); B.circle(300,612,18)   # sofas + round table
B.rrect(340,590,395,640,4)
B.label("LOUNGE + BAR",'15\'-10" X 26\'-8"',300.0,440.0); B.small("BAR",219,254,3.2)
# --- HOME THEATER (west half, south part) ---
B.rect(450,si+2,672,si+8,FURN,0.48); B.small("SCREEN",561,si+16,3.2)
for ry in (330,400):
    for i in range(4): B.rrect(462+i*54,ry,506+i*54,ry+34,4)
B.label("HOME THEATER",'15\'-6" X 16\'-10"',561.0,470.0)
# --- GYM / WELLNESS, SHOWER-WC, STORE ---
B.rect(450,520,470,600); B.rect(490,600,545,640)
B.label("GYM",'8\'-1" X 9\'-7"',502.0,560.0,7.0)
B.text("SHOWER",594,600,4.2); B.text("/ WC",594,606,4.2); B.text('2\'-10" X 9\'-7"',594,612,3.6)
B.replay(lambda it: R_(240,411.2,300,458).contains(it["drect"]) and purple(it), rot(270,430,180,594,640))   # WC at far end
B.replay(lambda it: R_(298,411.2,331,470).contains(it["drect"]) and purple(it), rot(316,452,-90,594,522))   # basin
B.line(572,560,617,560,FURN,0.48,dashes="[2 2] 0")
B.hatch(650,515,738,530); B.hatch(650,640,738,655)
B.label("STORE / AV",'7\'-8" X 9\'-6"',683.0,585.0,7.0); B.small("(EXISTING STAIRWELL, FLOORED OVER AT GF)",683,603,2.8)
# notes
ny=790
for t in ["NOTES (BASEMENT):","1. Existing stairwell to be floored over at ground floor level; the well below becomes the store.",
          "2. Existing north window converted to a glazed door: sill masonry removed, existing lintel retained.",
          "3. New external stair inside the existing sunken light well, approx. 10 risers, 3'-6\" wide, with canopy and floor trap.",
          "4. Existing ceiling height 8'-6\". Existing RCC columns and hidden beam on the centre line are retained; theater partition is non-load-bearing.",
          "5. No new opening in the ground floor slab. Existing basement windows and walls otherwise unchanged."]:
    B.note(t,150.5,ny,5.2); ny+=9
B.commit()
doc.save(OUT,garbage=1,deflate=True); print("saved",OUT,"pages",len(doc))
