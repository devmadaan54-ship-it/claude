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

# windows + glazed door to sunken court
B.window(E,536.0,ei,636.0)

B.window(195.0,ni,340.0,No)
B.door(345.0,ni,391.0,No,'x1','up')
B.small("GLAZED DOOR IN EXISTING",368,652,2.8); B.small("WINDOW OPENING, LINTEL RETAINED",368,656,2.8)
# sunken court + stair outside north wall
B.rect(190.0,No,513.0,754.0,BLACK,0.48,dashes="[3 2] 0")
B.stair(395.0,704.0,513.0,750.0,10,'right'); B.rect(345.0,704.0,395.0,750.0,MAG,0)
B.text("UP",454,748,5.0,color=MAG); B.text("SUNKEN GARDEN COURT",268,760,5.0); B.text("EXISTING LIGHT WELL, PLANTED",268,766,4.2)
B.line(120,No,1000,No,FURN,0.48,dashes="[4 2] 0"); B.text("PORCH ABOVE",560,700,5.0)
# --- LOUNGE + BAR (east half, by the windows) ---
B.rect(ei,si,262,262); B.rect(ei,262,202,330)                  # L bar counter
for cy in (275,300,322): B.circle(212,cy,5.5)
B.rect(262,si,420,262,FURN,0.48); B.small("WINE / DISPLAY WALL",341,251,3.0)
B.rrect(200,540,330,572,4); B.rrect(200,580,232,650,4); B.circle(300,612,18)   # sofas + round table
B.rrect(340,590,395,640,4)
B.labelr("LOUNGE + BAR",176,236,425,658,300.0,440.0); B.small("BAR",219,254,3.2)
# --- HOME THEATER (west half, south part) ---
B.rect(450,si+2,672,si+8,FURN,0.48); B.small("SCREEN",561,si+16,3.2)
for ry in (330,400):
    for i in range(4): B.rrect(462+i*54,ry,506+i*54,ry+34,4)
B.labelr("HOME THEATER",439,236,683,501,561.0,470.0)
# --- GYM / WELLNESS, SHOWER-WC, STORE ---
B.rect(450,520,470,600); B.rect(490,600,545,640)
B.labelr("GYM",439,507,566,658,502.0,560.0,7.0)

B.hatch(650,515,738,530); B.hatch(650,640,738,655)
B.labelr("STORE / AV",623,509,743,658,683.0,585.0,7.0); B.small("(EXISTING STAIRWELL, FLOORED OVER AT GF; COURTYARD PLANTER ABOVE)",683,603,2.6)
B.door(630.0,501.0,670.0,509.0,'x0','down')
B.text("SHOWER",594,600,4.2); B.text("/ WC",594,606,4.2); B.text(dimstr(572,507,617,658),594,612,3.6)
B.replay(lambda it: R_(240,411.2,300,458).contains(it["drect"]) and purple(it), rot(270,430,180,594,640))
B.replay(lambda it: R_(298,411.2,331,470).contains(it["drect"]) and purple(it), rot(316,452,-90,594,522))
B.line(572,560,617,560,FURN,0.48,dashes="[2 2] 0")
ny=790
for t in ["NOTES (BASEMENT):","1. Existing stairwell floored over at ground floor level; the well below is the store / AV room; the courtyard planter above it is waterproofed. The Brahmasthan above stays open.",
          "2. Basement entry by the stair in the west part of the existing north light well (north padas 3-4, outside the Brahmasthan and the north-east): north window opening converted to a glazed door, sill masonry removed, lintel retained.",
          "3. The servant room is at grade on the east side (see GF-PP-01), not at this level.",
          "4. Existing ceiling height 8'-6\". Existing RCC columns and hidden beam on the centre line are retained; theater partition is non-load-bearing.",
          "5. No new opening in the ground floor slab. Existing basement windows and walls otherwise unchanged."]:
    B.note(t,150.5,ny,5.2); ny+=9
