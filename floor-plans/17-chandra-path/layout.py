# ---------- 3. the new layout (sheet: top=SOUTH, bottom=NORTH, left=EAST, right=WEST) ----------
OL=lambda x0,y0,x1,y1: line(x0,y0,x1,y1,BLACK,0.96)
# --- walls ---
wall(437.4,492.9,484.3,511.8)                    # infill old kitchen door (15" wall)
OL(437.4,492.9,484.3,492.9); OL(437.4,511.8,484.3,511.8)          # its face lines
OL(394.3,511.8,402.1,511.8); OL(394.3,663.9,402.1,663.9)          # faces restored where partition removed
# --- kitchen (former bedroom-01 = SOUTH-EAST room of the house) ---
CD=31.6  # counter depth 2'-0"
rect(170.0,230.4,201.6,402.8)                    # east-wall counter leg (left wall)
rect(201.6,230.4,420.4,230.4+CD)                 # south-wall counter (top wall)
# hob: SE corner of kitchen, on east wall, cook faces EAST; clear of the window (starts y=278.8)
hx0,hy0=172.5,238.0; rect(hx0,hy0,hx0+26.5,hy0+34.0,FURN,0.48)
for (dx,dy) in ((7.5,8.5),(19,8.5),(7.5,25.5),(19,25.5)): circle(hx0+dx,hy0+dy,4.0)
# sink: NE corner of kitchen (bottom-left), on east leg below the window (ends y=357.2)
sx0,sy0=174.0,362.0; rrect(sx0,sy0,sx0+24.0,sy0+34.0,3.0,PURPLE,0.24); rrect(sx0+3,sy0+3,sx0+21,sy0+31,2.0,PURPLE,0.24); circle(sx0+21.5,sy0+17,1.6,PURPLE,0.24)
# fridge: SW corner of kitchen (top-right)
rect(384.4,262.0,420.4,298.0); line(384.4,280.0,420.4,280.0,FURN,0.48); line(414.4,262.0,414.4,298.0,FURN,0.48)
label("KITCHEN",'15\'-11" X 11\'-0"',300.0,325.0)
# --- toilet stays exactly where the architect placed it (EAST side, attached to bedroom, existing stack) ---
# --- merged bedroom (bedroom-02 + old kitchen, NORTH-EAST of house) ---
label("BEDROOM-01",'24\'-11" X 10\'-6"',430.0,600.0)
# bed group from old bedroom-01, rotated so the head is against the EAST wall (left), one side table dropped
def rot(cx,cy,deg,tx,ty):
    return pymupdf.Matrix(1,0,0,1,-cx,-cy)*pymupdf.Matrix(deg)*pymupdf.Matrix(1,0,0,1,tx,ty)
replay(lambda it: pymupdf.Rect(229,230.3,335,366).contains(it["drect"]) and it["type"]!="f",
       rot(282.0,297.0,-90, 237.0,592.0))
# wardrobe along the WEST end of the bedroom (right wall), hatch like original
wx0,wx1,wy0,wy1=535.0,561.4,511.8,663.9
rect(wx0,wy0,wx1,wy1,BLACK,0.48)
y=wy0+2.45
while y<wy1: line(wx0,y,wx1,y,BLACK,0); y+=2.45
