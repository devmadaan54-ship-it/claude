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
B.door(566.0,520.0,572.0,560.0,'y1','left')     # gym from basement lobby

# windows + glazed door to sunken court
B.window(E,536.0,ei,636.0)
B.small("EXISTING SERVANT ROOM AREA ON THE EAST SIDE (VERIFY ON SITE)",60,300,2.8); B.small("KEEPS ITS OWN ENTRY FROM THE EAST",60,305,2.8)
B.window(195.0,ni,391.0,No)
# sunken court + stair outside north wall
B.rect(190.0,No,395.0,754.0,BLACK,0.48,dashes="[3 2] 0"); B.text("EXISTING LIGHT WELL",292,725,5.0); B.text("PLANTED SUNKEN COURT",292,731,4.0)
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

B.rect(653,545,707,615,FURN,0.72); B.circle(680,580,17,FURN,0.48); B.circle(680,580,11,FURN,0.24)
B.stair(707,512,743,615,11,'down'); B.text("UP",725,608,4.0,color=MAG); B.small("11 R TO ENTRANCE",725,613,2.6,color=MAG)
B.rect(617,509,743,545,MAG,0); B.text("LANDING",680,530,4.0,color=MAG)
B.line(617,545,653,545,FURN,0.48,dashes="[2 2] 0"); B.small("GF FLIGHT OVER",635,580,2.6)
B.text("ENTRANCE ATRIUM",680,632,5.0); B.small("TREE PIT, SKYLIT VOID ABOVE",680,637,2.8)
B.door(617,515,623,545,'y0','left')
B.text("BASEMENT",594,600,4.6); B.text("LOBBY",594,606,4.6); B.text('2\'-10" X 9\'-7"',594,612,3.6)
B.door(575,501,610,509,'x0','up')
ny=790
for t in ["NOTES (BASEMENT):","1. Existing stairwell re-used as the entrance atrium: entrance door at porch level, 6 risers up to the ground floor and 11 down to this level, tree pit between the flights, basement lobby with doors to the gym and theater.",
          "2. No external basement stair; the light well on the north stays a planted sunken court with its window unchanged.",
          "3. Existing servant room area on the east side keeps its own entry; position to be verified on site.",
          "4. Existing ceiling height 8'-6\". Existing RCC columns and hidden beam on the centre line are retained; theater partition is non-load-bearing.",
          "5. No new opening in the ground floor slab. Existing basement windows and walls otherwise unchanged."]:
    B.note(t,150.5,ny,5.2); ny+=9
