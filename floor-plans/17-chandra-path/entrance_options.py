import pymupdf
from csedit import edit_page
from plan import *
SET="Proposed_Floor_Plan-20260916-R20-SET.pdf"; OUT="Entrance_Options-EO-01.pdf"
orig=pymupdf.open("proposed.pdf"); R_=pymupdf.Rect
ENT=[R_(515,684,760,850)]; GATE=[R_(28,935,225,975)]
def route(S,pts,color=RED):
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]): S.line(x0,y0,x1,y1,color,0.9,dashes="[5 3] 0")
    (x0,y0),(x1,y1)=pts[-2],pts[-1]; dx,dy=x1-x0,y1-y0; n=(dx*dx+dy*dy)**0.5; ux,uy=dx/n,dy/n
    S.poly([(x1,y1),(x1-8*ux+4*uy,y1-8*uy-4*ux),(x1-8*ux-4*uy,y1-8*uy+4*ux)],color,0,color)
def col(S): S.rect(624,690,636,702,BLACK,0.72,GREY)
def pool(S,x0,y0,x1,y1):
    S.rect(x0,y0,x1,y1,BLUE,0.48)
    for i in range(1,5): S.line(x0,y0+(y1-y0)*i/5,x1,y0+(y1-y0)*i/5,BLUE,0)
def landing(S): S.rect(560,684,717,745,MAG,0)
def make(option):
    doc=pymupdf.open(SET); doc.fullcopy_page(2); pg=doc[len(doc)-1]
    DEL=ENT+(GATE if option in (3,) else [])
    edit_page(doc,pg,DEL); S=Sheet(pg,orig[0]); col(S)
    if option==1:
        S.rect(560,684,717,812,MAG,0); S.stair(474,758,560,812,6,'right'); S.text("UP 6 R",517,822,4.0,color=MAG)
        S.rect(474,746,560,756,FURN,0.48); S.small("PLANTER WALL",517,743,2.4)
        pool(S,474,816,717,834); S.small("WATER CHANNEL 1'-2\" WIDE, FULL LENGTH OF THE PLATFORM",595,842,2.6)
        S.text("ARRIVAL PLATFORM",638,740,4.6); S.small(dimstr(560,684,717,812)+" AT +5'-0\"",638,746,3.0); S.small("SEATING BENCH + LANTERN",638,751,2.6)
        S.small("FLIGHT RISES WESTWARD BESIDE THE SUNKEN GARDEN: GUESTS CLIMB AS THEY WALK, THE DOOR OPENS AHEAD",520,860,2.8)
        route(S,[(120,930),(120,880),(430,880),(430,785),(470,785)]); route(S,[(560,785),(612,785),(612,692)])
    if option==2:
        S.rect(1095,942,1140,950,MAG,0); S.text("PEDESTRIAN GATE 3'-0\"",1117,962,4.0,color=MAG)
        S.rect(1095,590,1140,942,FURN,0.48); S.small("GARDEN PATH 3'-0\"",1117,760,2.8)
        pool(S,1146,600,1166,935); S.text("WATER",1156,590,3.0); S.text("CHANNEL",1156,595,3.0)
        S.stair(1095,585,1140,640,3,'left'); S.text("UP 3 R",1117,652,3.6,color=MAG)
        S.rect(1074.5,590,1091,636,(1,1,1),0,(1,1,1)); S.door(1074.5,590,1091,636,'y0','right'); S.small("NEW WEST DOOR",1060,582,2.6); S.small("INTO THE VESTIBULE",1060,587,2.6)
        S.text("WEST GARDEN ENTRY",1117,700,5.0); S.small("ARRIVAL THROUGH THE GARDEN, NOT THE DRIVEWAY",1117,708,2.8)
        S.text("PORCH: CARS ONLY",700,790,5.0); S.small("DROP-OFF AT THE LOBBY DOOR;",700,798,2.8); S.small("NO GRAND STAIR",700,803,2.8)
        route(S,[(1117,940),(1117,612),(1092,612)])
    if option==3:
        S.rect(540,942,697,950,MAG,0); S.text("CAR GATE 10'-0\" ON THE DOOR AXIS",618,962,4.0,color=MAG)
        S.line(40,935,197,957,RED,0.9); S.line(40,957,197,935,RED,0.9); S.text("EAST GATE CLOSED",118,968,3.4,color=RED)
        landing(S); S.stair(560,745,717,810,6,'up'); S.text("UP 6 R",638,820,4.0,color=MAG)
        pool(S,430,760,545,850); pool(S,732,760,847,850); S.small("REFLECTING POOL",487,858,2.6); S.small("REFLECTING POOL",789,858,2.6)
        S.line(638,940,638,812,BLACK,0.3,dashes="[6 3] 0"); S.small("AXIS: GATE, DRIVE, STAIR, DOOR",638,930,2.8)
        S.text("AXIAL ARRIVAL",638,880,5.0); S.small("HEAD-ON APPROACH; THE DOOR IS SEEN FROM THE GATE",638,888,2.8)
        route(S,[(600,940),(600,830),(638,830),(638,692)])
    if option==4:
        S.wall(470,684,478,796); S.wall(752,684,760,796); S.wall(470,788,585,796); S.wall(650,788,760,796)
        for x0,y0,x1,y1 in [(470,684,478,796),(752,684,760,796),(470,788,585,796),(650,788,760,796)]: S.rect(x0,y0,x1,y1,BLACK,0.48)
        S.line(585,792,646,780,BLACK,0.9); S.small("PIVOT GATE 4'-0\"",617,806,2.6)
        S.rect(560,684,717,730,MAG,0); S.stair(560,730,717,788,6,'up'); S.text("UP 6 R",638,760,3.4,color=MAG)
        S.circle(505,760,14,FURN,0.48); S.circle(505,760,9,FURN,0.24); S.small("TREE",505,780,2.4)
        S.circle(728,760,9,BLUE,0.48); S.small("WATER BOWL",728,780,2.4)
        S.text("ENTRY COURT",520,712,4.6); S.small(dimstr(478,684,752,788),520,718,3.0); S.small("WALLED 7'-0\" HIGH, OPEN TO SKY",520,723,2.6)
        S.small("DROP-OFF LANE "+dimstr(0,796,0,942)+" BETWEEN THE COURT AND THE GATE LINE",617,830,2.8)
        route(S,[(120,930),(120,870),(617,870),(617,798),(617,740)]); route(S,[(612,730),(612,692)])
    S.commit(); return doc,pg
sheet=pymupdf.open(); page=sheet.new_page(width=1684,height=1191)
def title(x,y,s,size,font=ARIALB,align=0):
    page.insert_text((x,y),s,fontsize=size,fontfile=font,fontname="F"+str(size))
title(40,50,"17 CHANDRA PATH  -  ENTRANCE OPTIONS  (EO-01)",20)
title(40,72,"GROUND FLOOR VIGNETTES, SAME ORIENTATION AS THE SET: TOP = SOUTH, BOTTOM = NORTH, LEFT = EAST. RED DASHED LINE = GUEST ROUTE FROM THE CAR TO THE FRONT DOOR.",9,ARIAL)
opts=[(1,"OPTION 1  -  TURNED ARRIVAL STAIR (RECOMMENDED)","Gate and door stay. The flight rises westward beside the sunken garden and lands on a 10' x 8'-2\" arrival platform in front of the door. A planter wall and water channel edge the stair. Least change, no Vastu shift, drop-off stays under cover.",R_(20,640,900,1000)),
      (2,"OPTION 2  -  WEST GARDEN ENTRY","A 3' pedestrian gate west of the lobby block, a garden path beside a water channel, three steps up to a new west door into the vestibule. The porch keeps only cars. West door in the north half is Vastu-acceptable.",R_(560,470,1400,1000)),
      (3,"OPTION 3  -  AXIAL ARRIVAL","The car gate moves to the middle of the north boundary, on the axis of the straight stair and the door; reflecting pools flank the flight. Most formal; costs the east-end gate position.",R_(20,640,900,1000)),
      (4,"OPTION 4  -  WALLED ENTRY COURT","A 17'-5\" x 6'-8\" forecourt centred on the door, 7' walls, a pivot gate on the axis, a tree and a water bowl inside, the stair within the court. Cars pass in a 9'-3\" lane along the gate line; drop-off at the pivot gate.",R_(20,640,900,1000))]
for i,(n,t,desc,clip) in enumerate(opts):
    doc,pg=make(n); pix=pg.get_pixmap(matrix=pymupdf.Matrix(3,3),clip=clip)
    cx=40+(i%2)*822; cy=95+(i//2)*520; W=800; H=W*clip.height/clip.width
    if H>400: H=400; W=H*clip.width/clip.height
    page.insert_image(R_(cx,cy+22,cx+W,cy+22+H),pixmap=pix); page.draw_rect(R_(cx,cy+22,cx+W,cy+22+H),color=(0,0,0),width=0.5)
    title(cx,cy+14,t,12)
    page.insert_textbox(R_(cx,cy+H+30,cx+800,cy+H+100),desc,fontsize=8.5,fontfile=ARIAL,fontname="Fd")
sheet.save(OUT); print("saved",OUT)
