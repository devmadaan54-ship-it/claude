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
]
page=doc.new_page(width=W,height=H)
y=M
def new_page():
    global page,y
    page=doc.new_page(width=W,height=H); y=M
page.insert_text((M,y+14),"17 CHANDRA PATH  |  LUXURY HOTEL-INSPIRED DESIGN BRIEF",fontsize=13,fontname="hebo"); y+=24
page.insert_text((M,y+10),"Companion to drawings BF-PP-01 and GF-PP-01 (revision R2, 16-09-2026). Items marked 'drawn' are on the sheets; the rest are specification.",fontsize=8,fontname="helv",color=(0.3,0.3,0.3)); y+=22
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
