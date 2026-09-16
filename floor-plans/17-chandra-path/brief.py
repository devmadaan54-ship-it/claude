import pymupdf
OUT="17-Chandra-Path-Luxury-Design-Brief.pdf"
doc=pymupdf.open()
W,H=595,842; M=48
sections=[
("ARRIVAL, PORCH AND ENTRANCE", [
 "Porte-cochere feel at the porch: a slatted timber or fin canopy over the drop-off zone in front of the verandah, with recessed step lights along the edge.",
 "Sunken garden court at the north-east corner of the porch (the existing basement light well), planted with gravel, a small ornamental tree and boulders, and lit at night. The external basement stair runs inside it (drawn on BF-PP-01 and GF-PP-01).",
 "Entrance foyer treated as a hotel lobby: stone floor, a single feature pendant, console with a mirror, concealed shoe storage in the vestibule, and a 3-scene lighting preset at the door (arrive, evening, night).",
 "Vastu: the arrival is on the north, which is favourable. A shallow water bowl in the sunken court adds water in the north-east, which is auspicious.",
]),
("GREAT ROOM AND DINING", [
 "Layered lighting: cove uplight, low-glare downlights over the dining table, and a dimmable feature pendant. All on scenes.",
 "Motorised sheer and blackout blinds on the garden-facing glazing with wall keypads and app control.",
 "Concealed AV: in-ceiling speakers, a hidden projector or a framed TV that reads as art when off.",
 "Pergola lounge in the west garden over the architect's outdoor seating (drawn on GF-PP-01): slatted timber roof, low deep sofa, round stone coffee table, as in the reference courtyard image.",
]),
("KITCHEN (south-east room)", [
 "Chef's kitchen with a 6 ft x 3 ft breakfast island and two stools (drawn). No hob or sink on the island, which keeps the Vastu centre of the room clear.",
 "Hob on the east wall so the cook faces east, sink in the north-east corner, fridge in the south-west corner (drawn). Chimney over the hob; the east window is above the counter.",
 "Hotel-grade fittings: quartz or stone counters with a matching splashback, integrated appliances behind panels, a built-in coffee station and wine cooler, drawer lighting, and a pantry run of tall units on the west wall.",
 "Herb court outside the east window (drawn): a small gravel court with planters so the kitchen looks onto green.",
]),
("MASTER SUITE: BEDROOM, DRESSING, BATHROOM", [
 "Suite sequence as in Aman and Bulgari suites: bedroom, then a separate dressing room, then the bathroom, with the bathroom opening to a private outdoor court.",
 "Bedroom (16'-5\" x 10'-6\"): bed with its head on the south wall, which is the top Vastu direction and a solid wall. Bedside tables both sides with master controls for lights, blinds and the do-not-disturb light at the door. Lounge chair and side table, writing desk under the north window, low TV console (drawn).",
 "Wall-to-wall upholstered headboard, sheer plus blackout motorised curtains, dimmable bedside reading lights, underfloor cooling or a quiet ducted AC with no visible grilles, and acoustic door seals.",
 "Dressing room (8'-0\" x 10'-4\"): wardrobe run on the south wall, a second run against the partition, a dressing table with a lit mirror on the east wall, and a full-height sliding glass door into the private garden court (drawn). Luggage bench, safe and a minibar/pantry cabinet inside the dressing.",
 "Private garden court (east side yard, about 5'-9\" x 13'): walled gravel court with boulders and a small tree, seen from the bed through the glass door, as in the reference bedroom image. Vastu: north-east court kept open, light and planted; no storage there.",
 "Bathroom (existing 10'-3\" x 5'-3\", position unchanged): wet zone at the east end behind a fixed glass screen (drawn), with a ceiling rain head plus hand shower, a built-in stone or microcement bath under the rain head if a tub is wanted, wall-hung WC facing north, and a monolithic stone vanity with a backlit mirror. Heated towel rail, floor drain, and non-slip stone floor.",
 "Bath court: the bathroom's east window becomes full-height fixed glazing onto a small walled court with an outdoor rain shower on the boundary wall (drawn), giving the open-to-sky shower from the reference images without touching the structure above.",
 "Materials palette from the references: board-formed concrete or lime-plaster walls, ribbed or fluted tiles, warm timber, brushed brass or bronze fittings, and honed natural stone.",
]),
("BASEMENT (BF-PP-01)", [
 "Lounge and bar on the east half beside the windows: L-shaped bar with three stools, wine display wall, deep sofas and a round table. This is the social room and the daylight comes through the light-well windows.",
 "Home theater on the west half: fully enclosed acoustic partition on the existing column line, screen on the south wall, two rows of four recliners, tiered floor if height allows (ceiling is 8'-6\"), fabric-wrapped walls and blackout.",
 "Gym with an attached shower and WC (hotel wellness style), and a store / AV rack room in the old stairwell, which is floored over at ground level.",
 "Entry by the external stair in the sunken court through a new glazed door in the existing north window opening. The existing lintel stays; only the sill masonry comes out.",
 "Vastu: basement under the east / north-east half is acceptable; dark and heavy uses (theater, store) are on the west and north-west; the north-east light well stays open and planted.",
]),
("WHOLE-HOUSE SYSTEMS", [
 "Lighting control with scenes in every room, warm-dim LEDs (2200K to 3000K), and night-path lighting from the bed to the bathroom.",
 "Automation for blinds, lighting, AC and audio from bedside keypads and phones. Door sensors for the do-not-disturb / make-up-room indicators if staff service the rooms.",
 "Water: pressure-boosted hot water with recirculation so rain showers run hot immediately; water softening; outdoor showers on the same loop.",
 "Acoustics: solid-core doors with drop seals on the bedroom, bathroom and theater; acoustic underlay on the first floor over the bedroom.",
 "Structure: none of the above touches the stone and brick piers marked 1 to 8. New work is partitions, joinery, glazing in existing openings, and the external stair in the existing light well.",
]),

("COURTYARD-01 AND THE CENTRAL VOID", [
 "Courtyard-01 (5'-7\" x 9'-1\") sits in the old stairwell shaft beside the entrance foyer and is open to sky through the first, second and terrace floors. No new slab is cut: the shaft already exists. A single tree stands in a 3 ft deep waterproofed planter over the basement store, with gravel, a bench and uplighting.",
 "Each upper floor keeps a 5'-6\" walkway on the east side of the void with a frameless glass balustrade; on the second floor this walkway is the family picture gallery, lit by daylight from the void.",
 "Vastu: the void is just north of the centre of the house. An open, planted, light centre-north is favourable, and the tree is kept small and single-stemmed.",
]),
("FIRST FLOOR (FF-PP-01)", [
 "Three bedrooms: the master suite stays in the south-west (the Vastu master position), Bedroom-01 stays in the south-east with the park view, and Bedroom-03 with its own toilet is new in the north wing over the porch.",
 "Master suite upgraded to a hotel suite: the former west terrace is enclosed as an 8'-3\" x 10'-5\" walk-in closet with wardrobe runs on both long walls and a central island, entered from the bedroom and connecting straight into the bathroom. The small south-west terrace stays as the private terrace.",
 "The large north-east room becomes the study and memento room (17' x 13'-10\"): desk facing the east bay for video calls with the garden behind, memento shelving, a two-seat sofa, and a book wall. The puja room (5'-7\" x 4'-8\") is carved from its north-east corner with the altar on the east wall, which is the ideal Vastu position for both uses.",
 "North-east garden terrace (6'-9\" x 12'-5\") at the east end of the new wing, planted and open, reached from the study and from Bedroom-03. This keeps the north-east light and low as Vastu asks.",
]),
("SECOND FLOOR (SF-PP-01)", [
 "The south-east toilet, walk-in closet and Bedroom-02 are removed. The whole south and east area becomes one semi-open lounge with a bar, and a view verandah at the south-east where the best view is. Existing structural wall lines stay as piers with wide lintel openings.",
 "Bedroom-02 and its toilet move to the north wing over the porch, with the same north-east garden terrace as the floor below. The master suite on this floor is unchanged.",
 "Family gallery along the courtyard void; luggage room kept as a store.",
]),
("TERRACE FLOOR (TF-PP-01)", [
 "Full roof terrace with a 3'-6\" parapet, the courtyard void railed as a skylight opening, solar array along the south parapet, water tanks and plant in the south-west, pergola sky lounge on the east and a bar at the south-east. The north-east is kept open and low.",
 "Staff room (7' x 7') with WC and a screened clothes-drying yard beside the stair and lift mumty in the north-west, which is the Vastu position for staff quarters and services.",
]),
("EAST SERVICE WING AND THE PARK SIDE", [
 "The east boundary wall is to be rebuilt straight and parallel to the house at the widest existing offset, which leaves a 4'-6\" strip. If the survey allows the wall at the narrower south-end line instead, the strip becomes 7' and every room below grows accordingly.",
 "The strip is a single-storey service wing running the full east side: staff toilet, utility with washing machine and sink (door cut below the existing kitchen window), a small planted bath court with the outdoor shower, a store, and a green court with planters and a small tree outside the dressing room's glass door.",
 "Its roof is at 7'-6\" with a continuous planter parapet, so the kitchen, bathroom and dressing look at greenery towards the park side rather than at a wall.",
 "Concealed event gate in the east boundary wall along the porch: flush wall-finished panels on concealed pivots so the wall reads as solid from outside and opens for events.",
]),
("VASTU VERDICTS ON THE REQUESTS", [
 "Bedroom in the north-east on the first floor: not aligned. Vastu keeps the north-east open; the north-east room is used as study and puja instead, and the third bedroom is in the north, which is acceptable.",
 "Master bedroom in the south-east for the view: not aligned. The south-east is the fire corner and is kept for the kitchen below and Bedroom-01 above; the master stays in the south-west.",
 "Second floor bedroom and toilet in the north: aligned, with the toilet on the west side of the bedroom.",
 "Puja in the north-east: aligned, placed on the first floor where the north-east corner is a quiet room; on the ground floor that corner is the bedroom dressing, which is not suitable.",
 "Basement under the east half, sunken court in the north-east, central courtyard north of centre, staff quarters and water tanks: all aligned.",
]),
]
page=doc.new_page(width=W,height=H)
y=M
def new_page():
    global page,y
    page=doc.new_page(width=W,height=H); y=M
page.insert_text((M,y+14),"17 CHANDRA PATH  |  LUXURY HOTEL-INSPIRED DESIGN BRIEF",fontsize=13,fontname="hebo"); y+=24
page.insert_text((M,y+10),"Companion to drawings BF, GF, FF, SF and TF-PP-01 (revision R4, 16-09-2026). Items marked 'drawn' are on the sheets; the rest are specification.",fontsize=8,fontname="helv",color=(0.3,0.3,0.3)); y+=22
page.insert_textbox(pymupdf.Rect(M,y,W-M,y+40),"Sources for the hotel benchmarks: Aman villa standards (large tubs, twin vanities, dressing areas, outdoor showers, sunken baths, private courtyard gardens) and Bulgari Hotel Milano suites (separate bedroom with walk-in closet, bath with tub and shower).",fontsize=7.5,fontname="helv",color=(0.3,0.3,0.3),lineheight=1.25); y+=32
for title,items in sections:
    need=18+sum(1 for _ in items)*12
    if y+40>H-M: new_page()
    page.insert_text((M,y+11),title,fontsize=10.5,fontname="hebo"); y+=18
    for it in items:
        r=pymupdf.Rect(M+12,y,W-M,y+200)
        h=page.insert_textbox(r,"•  "+it,fontsize=8.6,fontname="helv",lineheight=1.25)
        used=200-h
        if y+used>H-M:
            # undo by re-drawing on a new page: simple approach, leave and continue on next page
            new_page(); r=pymupdf.Rect(M+12,y,W-M,y+200); h=page.insert_textbox(r,"•  "+it,fontsize=8.6,fontname="helv",lineheight=1.25); used=200-h
        y+=used+3
    y+=8
doc.save(OUT); print("saved",OUT,len(doc),"pages")
