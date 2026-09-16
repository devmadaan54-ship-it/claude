# ---------- 3. the new layout ----------
# --- walls ---
wall(150.5,402.8,220.0,410.7); wall(259.5,402.8,345.4,410.7)   # kitchen/utility partition with new door gap
wall(252.4,492.9,291.5,500.7)                    # infill old toilet door (partition, 6")
wall(437.4,492.9,484.3,511.8)                    # infill old kitchen door (15" wall)
wall(257.0,500.7,264.9,548.0); wall(257.0,587.5,264.9,663.9)   # new toilet partition with door gap
OL=lambda x0,y0,x1,y1: line(x0,y0,x1,y1,BLACK,0.96)
OL(252.4,492.9,291.5,492.9); OL(252.4,500.7,291.5,500.7)          # old toilet door infill faces
OL(437.4,492.9,484.3,492.9); OL(437.4,511.8,484.3,511.8)          # old kitchen door infill faces
OL(394.3,511.8,402.1,511.8); OL(394.3,663.9,402.1,663.9)          # faces restored where partition removed
OL(257.0,500.7,257.0,548.0); OL(264.9,500.7,264.9,548.0)          # new toilet partition faces
OL(257.0,587.5,257.0,663.9); OL(264.9,587.5,264.9,663.9)
# --- doors ---
door(257.0,548.0,264.9,587.5,'y0','left')        # toilet door: hinge top, swings into toilet (west)
door(220.0,402.8,259.5,410.7,'x0','down')        # utility door from kitchen: hinge west, swings into utility
# --- kitchen (former bedroom-01, SW of house) ---
CD=31.6  # counter depth 2'-0"
rect(170.0,230.4,420.4,230.4+CD)                 # south counter (top wall)
rect(388.8,230.4+CD,420.4,352.6)                 # east counter leg (SE corner -> hob)
rect(265.0,402.8-CD,340.0,402.8)                 # north counter (sink)
line(170.0,230.4+CD,170.0,230.4+CD)              # (no-op guard)
# hob on east leg, cook faces east
hx0,hy0=392.5,268.0; rect(hx0,hy0,hx0+24.5,hy0+34.0,FURN,0.48)
for (dx,dy) in ((6.5,8.5),(18,8.5),(6.5,25.5),(18,25.5)): circle(hx0+dx,hy0+dy,4.0)
# sink on north counter (NE side of kitchen)
sx0,sy0=292.0,375.0; rrect(sx0,sy0,sx0+34.0,sy0+22.0,3.0,PURPLE,0.24); rrect(sx0+3,sy0+3,sx0+31,sy0+19,2.0,PURPLE,0.24); circle(sx0+17,sy0+19.5,1.6,PURPLE,0.24)
# fridge (west side, below window)
rect(170.0,362.0,206.0,398.0); line(170.0,380.0,206.0,380.0,FURN,0.48); line(200.0,362.0,200.0,398.0,FURN,0.48)
label("KITCHEN",'15\'-11" X 11\'-0"',290.0,318.0)
# --- utility / store (old toilet strip) ---
label("UTILITY / STORE",'10\'-3" X 5\'-3"',252.0,462.0)
# wash sink reuse: old basin cluster translated to west end
replay(lambda it: pymupdf.Rect(298,411.2,331,470).contains(it["drect"]) and it.get("color") and abs(it["color"][0]-0.35294)<0.01,
       pymupdf.Matrix(1,0,0,1, 0, 15))
# --- merged bedroom (bedroom-02 + old kitchen, NW of house) ---
label("BEDROOM-01",'18\'-11" X 10\'-6"',337.0,600.0)
# bed group from old bedroom-01 (bed, side tables, rug, figure), head to south wall
replay(lambda it: pymupdf.Rect(177,230.3,388,366).contains(it["drect"]) and it["type"]!="f" and not pymupdf.Rect(177,230,229,251).contains(it["drect"]),
       pymupdf.Matrix(1,0,0,1, 168.0, 281.4))
# wardrobe along west partition (hatch like original)
wx0,wx1,wy0,wy1=264.9,291.2,548.0,663.9
rect(wx0,wy0,wx1,wy1,BLACK,0.48)
y=wy0+2.45
while y<wy1: line(wx0,y,wx1,y,BLACK,0); y+=2.45
# --- new toilet (NW corner, west strip) ---
label("TOILET",'5\'-6" X 10\'-5"',229.0,606.0)
# WC: old cluster (x 240-300, y 411-458) rotated -90 (CCW) to sit on west wall facing east
def rot(cx,cy,deg,tx,ty):
    return pymupdf.Matrix(1,0,0,1,-cx,-cy)*pymupdf.Matrix(deg)*pymupdf.Matrix(1,0,0,1,tx,ty)
wc_sel=lambda it: pymupdf.Rect(240,411.2,300,458).contains(it["drect"]) and it.get("color") and abs(it["color"][0]-0.35294)<0.01
replay(wc_sel, rot(270,430,-90, 186.5,578.0))
# basin: old cluster on east wall (x 298-331) rotated -90 so back is to the top (south) wall
basin_sel=lambda it: pymupdf.Rect(298,411.2,331,470).contains(it["drect"]) and it.get("color") and abs(it["color"][0]-0.35294)<0.01
replay(basin_sel, rot(316,452,-90, 196.0,514.0))
# shower: old cluster at west end (x<232, y>455) translated to bottom of new toilet
sh_sel=lambda it: pymupdf.Rect(170.5,455,235,501).contains(it["drect"]) and it.get("color") and abs(it["color"][0]-0.35294)<0.01
replay(sh_sel, pymupdf.Matrix(1,0,0,1, 0, 168.0))
text("SHOWER",236.0,640.0,3.2); text("AREA",236.0,644.5,3.2)
line(170.0,621.0,257.0,621.0,FURN,0.48,dashes="[2 2] 0")   # shower partition line (glass)
