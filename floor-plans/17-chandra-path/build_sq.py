import pymupdf
from csedit import edit_page
from plan import *
SRC="Proposed_Floor_Plan-20260916-R17.pdf"; OUT="Servant_Quarters-SQ-PP-01.pdf"
doc=pymupdf.open(SRC); orig=pymupdf.open("proposed.pdf")
R_=pymupdf.Rect
def toilet_symbols(S, wc=None, basin=None, shower=None):
    if wc: S.replay(lambda it: R_(240,411.2,300,458).contains(it['drect']) and purple(it), rot(270,430,wc[0],wc[1],wc[2]))
    if basin: S.replay(lambda it: R_(298,411.2,331,470).contains(it['drect']) and purple(it), rot(316,452,basin[0],basin[1],basin[2]))
    if shower: S.replay(lambda it: R_(170.5,455,235,501).contains(it['drect']) and purple(it), rot(200,478,shower[0],shower[1],shower[2]))
# template from the GF sheet (page 1 of R17 = GF): copy, clear plan, retitle
doc.fullcopy_page(1); pg=doc[len(doc)-1]
edit_page(doc,pg,[R_(34,26,1640,1166)],TEXTDEL=[R_(34,26,1640,1166),R_(1390,630,1600,675),R_(1396,828,1470,846)])
S=Sheet(pg,orig[0])
S.text("SERVANT QUARTERS -",1392.8,648.0,17.09,align="left",fontpath=ARIALB); S.text("GRADE LEVEL LAYOUT",1392.4,668.5,17.09,align="left",fontpath=ARIALB); S.text("SQ-PP-01",1398.1,840.5,14.12,align="left",fontpath=ARIAL)
# ---- context: house east wall (reference) ----
XW=150.5-109.9; PL=XW-11.8
S.wall(150.5,207,170,683.6); S.OL(150.5,207,150.5,683.6); S.OL(170,207,170,683.6)
S.wall(150.5,207,420,230.4); S.OL(150.5,230.4,420,230.4)
S.wall(150.5,663.9,600,683.6); S.OL(150.5,663.9,600,663.9)
S.text("HOUSE (GROUND FLOOR AT +5'-0\")",300,300,6.0); S.text("KITCHEN OVER THIS STRETCH: NO SLAB ABOVE THE SERVANT ROOM UNTIL THE FIRST-FLOOR BAY",300,309,3.6)
S.text("TOILET + DRESSING OVER THIS STRETCH: BATH DECK AND PLANTED STRIP AT +5'-0\" ABOVE THE RESTROOM AND KITCHENETTE",300,520,3.6)
S.text("PORCH (+1'-6\")",300,720,6.0)
S.line(PL,195,PL,760,BLACK,0.48,dashes="[6 2 1 2] 0")
S.wall(PL,207,XW,700); S.OL(PL,207,PL,700); S.OL(XW,207,XW,700)
S.wall(XW,207,150.5,213); S.OL(XW,207,150.5,207); S.OL(XW,213,150.5,213)
S.dimline(XW,196,150.5,196,size=3.6); S.small("CLEAR; BOUNDARY WALL 10'-0\" HIGH, 9\" THICK",96,203,2.4)
# ---- grade-level plan, floor sunk to -3'-0" ----
# entry from the porch end: door at porch level, 9 risers down inside along the wall
S.wall(XW,683.6,150.5,689); S.OL(XW,683.6,150.5,683.6); S.OL(XW,689,150.5,689)
S.door(48,683.6,86,689,'x0','up')
S.stair(XW,596,80,676,9,'up'); S.text("DN 9 R",60,690+6,3.6,color=MAG); S.small("+1'-6\" TO -3'-0\"",60,701,2.4,color=MAG)
S.wall(80,596,85,676); S.OL(80,596,80,676); S.OL(85,596,85,676)
S.text("ENTRY",117,640,4.6); S.small(dimstr(85,596,150.5,683.6),117,645,2.6)
S.rect(118,600,150.5,640,FURN,0.48); S.small("SHOE / LOCKERS",134,647,2.4)
# north band: kitchenette + dining under the planted strip
S.wall(XW,590,150.5,596); S.OL(XW,590,150.5,590); S.OL(XW,596,150.5,596)
S.door(90,590,125,596,'x0','up')
S.rect(122,488,150.5,585); S.line(122,520,150.5,520,FURN,0.48); S.circle(136,504,7,PURPLE,0.24); S.rect(126,540,146,560,FURN,0.48)
S.small("SINK",136,498,2.4); S.small("HOB",136,566,2.4)
S.rect(XW,488,60,585,FURN,0.48); S.line(XW,520,60,520,FURN,0.48); S.line(XW,552,60,552,FURN,0.48); S.small("LOCKERS",50,592-8,2.4)
S.rect(72,530,110,560,FURN,0.48); S.circle(66,545,5); S.circle(116,545,5)
S.text("KITCHENETTE",91,505,4.6); S.text("+ DINING",91,511,4.6); S.small(dimstr(XW,488,150.5,590),91,516,2.6); S.small("FLOOR -3'-0\", CEILING +4'-6\" (7'-6\" CLEAR)",91,521,2.2)
# middle band: restroom beside the house, path along the wall
S.wall(XW,483,150.5,488); S.OL(XW,483,150.5,483); S.OL(XW,488,150.5,488)
S.wall(80,405,85,483); S.OL(80,405,80,483); S.OL(85,405,85,483)
S.wall(XW,400,150.5,405); S.OL(XW,400,150.5,400); S.OL(XW,405,150.5,405)
S.door(80,420,85,452,'y0','right')
toilet_symbols(S, wc=(90,125,420), basin=(90,100,470), shower=(0,132,470))
S.line(85,452,150.5,452,FURN,0.48,dashes="[2 2] 0")
S.text("RESTROOM",117,440,4.2); S.small(dimstr(85,405,150.5,483),117,445,2.6); S.small("WC + SHOWER, EXISTING DRAIN",117,450,2.2)
S.text("PATH",60,445,3.6); S.small(dimstr(XW,405,80,483),60,450,2.4)
S.door(90,483,125,488,'x0','up')                                    # kitchenette band -> path/restroom band
S.door(45,400,80,405,'x0','up')                                     # path -> sleeping room
# south room: sleeping room, double height with mezzanine
S.rect(52,216,99,314,FURN,0.48); S.line(52,236,99,236,FURN,0.48)
S.rect(103,216,150,314,FURN,0.48); S.line(103,236,150,236,FURN,0.48)
S.hatch(XW,380,110,400)
S.rect(114,340,150.5,398,MAG,0); S.stair(114,340,150.5,398,8,'down'); S.text("UP TO",132,328,3.0,color=MAG); S.text("MEZZANINE",132,333,3.0,color=MAG)
S.rect(XW+3,300,148,398,BLACK,0.48,dashes="[3 2] 0"); S.small("MEZZANINE OVER, 2 BEDS, FLOOR +7'-0\"",95,308,2.4)
S.text("SLEEPING ROOM",96,262,4.6); S.small(dimstr(XW,213,150.5,400),96,267,2.8); S.small("2 BEDS + 2 ON MEZZANINE = 4",96,272,2.4); S.small("FLOOR -3'-0\", DOUBLE HEIGHT TO +15'-0\"",96,277,2.2)
S.window(PL,240,XW,300); S.small("WINDOW TO PARK",34,320,2.4)
# ---- sections (schematic), 15.7 units per foot ----
def section(x0,ybase,title,deck):
    s=15.7
    L=lambda ft: ybase-ft*s
    S.text(title,x0+120,ybase-16.5*15.7-14,6.0)
    S.line(x0-20,L(0),x0+260,L(0),BLACK,0.48,dashes="[3 2] 0"); S.small("GRADE 0",x0-10,L(0)-3,2.4)
    S.wall(x0,L(10),x0+12,L(-3.5)); S.small("BOUNDARY WALL 10'",x0+6,L(10)-4,2.4)
    S.wall(x0+12+110,L(-3.5),x0+12+110+20,L(16)); S.small("HOUSE",x0+132,L(16)-4,2.6)
    S.line(x0+12,L(-3),x0+122,L(-3),BLACK,0.96); S.small("SERVANT FLOOR -3'-0\"",x0+67,L(-3)+6,2.4)
    S.line(x0+122,L(5),x0+200,L(5),BLACK,0.96); S.small("GROUND FLOOR +5'-0\"",x0+180,L(5)-3,2.4)
    if deck:
        S.wall(x0+12,L(4.5),x0+122,L(5)); S.small("DECK / PLANTED STRIP +5'-0\"",x0+67,L(5)-4,2.4)
        S.line(x0+67,L(-3),x0+67,L(4.5),BLACK,0.3); S.small("7'-6\" CLEAR",x0+75,L(1),2.4)
    else:
        S.line(x0+40,L(7),x0+122,L(7),BLACK,0.96); S.small("MEZZANINE +7'-0\"",x0+81,L(7)-3,2.4)
        S.wall(x0+12,L(15),x0+122,L(15.5)); S.small("ROOF +15'-0\" (BELOW FIRST-FLOOR BAY)",x0+67,L(15)-4,2.4)
        S.line(x0+26,L(-3),x0+26,L(15),BLACK,0.3); S.small("18'-0\"",x0+34,L(6),2.4)
        S.line(x0+81,L(7),x0+81,L(15),BLACK,0.3); S.small("8'-0\"",x0+89,L(11),2.4)
        S.line(x0+81,L(-3),x0+81,L(7),BLACK,0.3); S.small("10'-0\"",x0+89,L(2),2.4)
    S.wall(x0+122,L(15.5),x0+200,L(16)); S.small("FIRST-FLOOR BAY",x0+160,L(16)-4,2.4)
section(760,560,"SECTION A-A THROUGH SLEEPING ROOM",False)
section(1100,560,"SECTION B-B THROUGH KITCHENETTE / RESTROOM",True)
S.line(XW-8,250,150.5+8,250,BLACK,0.48,dashes="[4 2] 0"); S.text("A",XW-14,252,4.0); S.text("A",150.5+14,252,4.0)
S.line(XW-8,540,150.5+8,540,BLACK,0.48,dashes="[4 2] 0"); S.text("B",XW-14,542,4.0); S.text("B",150.5+14,542,4.0)
ny=800
for t in ["NOTES (SERVANT QUARTERS):","1. EXISTING SERVANT ROOM AND RESTROOM DEMOLISHED; STRIP REBUILT WITH ITS FLOOR AT -3'-0\" THROUGHOUT (RETAINING WALLS, WATERPROOFED, SUMP + PUMP FOR DRAINAGE).",
          "2. ENTRY FROM THE PORCH END ONLY, 9 RISERS DOWN INSIDE THE DOOR; NO DOOR INTO THE HOUSE.",
          "3. SLEEPING ROOM IS DOUBLE HEIGHT (NO SLAB ABOVE UNTIL THE FIRST-FLOOR BAY): 2 BEDS BELOW, MEZZANINE AT +7'-0\" WITH 2 MORE BEDS, LADDER STAIR IN THE CORNER. ROOF AT +15'-0\" WITH A LOUVRED VENT.",
          "4. RESTROOM AND KITCHENETTE SIT UNDER THE GROUND-FLOOR BATH DECK AND PLANTED STRIP (+5'-0\"), 7'-6\" CLEAR; RESTROOM ON THE EXISTING DRAIN, HIGH-LEVEL VENT TO THE PATH.",
          "5. PATH 2'-6\" ALONG THE BOUNDARY WALL, OPEN ABOVE WHERE NO DECK; WINDOW TO THE PARK IN THE SLEEPING ROOM AS EXISTING. ALL DIMENSIONS ARE CLEAR INTERNAL SIZES."]:
    S.note(t,300,ny,5.0); ny+=8
S.commit()
out=pymupdf.open(); out.insert_pdf(doc,from_page=len(doc)-1,to_page=len(doc)-1); out.save(OUT); print("saved",OUT)
