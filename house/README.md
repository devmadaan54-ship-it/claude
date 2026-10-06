# 17 Chandra Path: working model of the house

This folder turns the architect's PDF (`source/17C_original.pdf`) into a format
that can be read, discussed and changed one step at a time.

| File | What it is |
|---|---|
| `model.yaml` | **The house as it exists.** Every room, wall, door, window, stair and fixture on all 4 floors, with coordinates in feet. Only corrected, never redesigned. |
| `plan.html` | Drawing of `model.yaml`. |
| `design_v1.yaml` | **Design iteration 1 (Vastu changes)**, written as a list of changes on top of `model.yaml`: what is removed, modified and added, plus a change log with the reason and the structural note for each change. |
| `design_v1.html` | Drawing of design v1. Includes the change log, the Vastu 3x3 grid, a table of which zone each WC, stair, lift and entrance falls in, and a toggle that shows the existing walls underneath. New walls are teal. |
| `render.py` | Builds all the HTML files: `python3 house/render.py`. |
| `source/17C_original.pdf` | The original drawing, kept for reference. |

## How iterations work

Each design round is a new `design_vN.yaml` with `base:` pointing at the
previous one (v1 starts from `model.yaml`). It lists only what changes:

```yaml
base: design_v1.yaml
remove: [gf.w.some_wall]
modify: {gf.kitchen_new: {box: [1.25, 1.15, 17.22, 12.18]}}
add: {ground: {walls: [...], rooms: [...]}}
changes: [{what: ..., why: ..., structure: ...}]
```

So every version stays readable on its own, and you can always see exactly
what moved between rounds.

## How the model works

- **Units:** feet in decimals (16'-6" = 16.5). The architect's written sizes are kept as `label`s.
- **One shared frame for all floors**, so things stack: (0,0) is the top-left outer corner of the ground floor walls. x goes right, y goes down.
- **Directions:** "up / down / left / right" mean on the drawing. From the compass on the sheets: **up = East** (rear boundary), **right = South** (front lawn and porch), **down = West** (parking and gates), **left = North** (store and basement entry strip).
- Every element has an **id** (for example `gf.w.office_top`, `ff.bedroom3`, `gf.o.main_door`). Turn on "element ids" in `plan.html` to see them. Prefixes: `b.` basement, `gf.` ground, `ff.` first, `t.` terrace; `.w.` wall, `.o.` opening, `.f.` fixture, `.a.` annotation.
- **Accuracy:** room sizes match the written dimensions. Wall positions are measured off the drawing and are good to about ±4 inches. The terrace sheet is drawn less carefully (about ±2 ft against the floors below).

## The house in words

**Site.** The plot is 82'-5" x 47'-0" (3,820.73 sq ft). The house is 55'-7" wide and about 30' deep, built against the east (top) boundary. A 7' strip on the north (left) side is the store and basement entry. The front porch and the front lawn (about 19'-10" deep) are on the south (right). Parking takes the whole west (bottom) side, 15'-6" to 16'-10" deep, at FFL +18", with two gates in the west boundary wall: one at the store-strip end and one at the porch end.

**Basement** (1,080.76 sq ft, ceiling 8'-6"). It sits under the north half of the house. It is one space split by two columns and a light partition into a **Theater** (15'-8" x 26'-8") on the left and a **Hall** (17'-0" x 26'-8") on the right, with a door between them. The stair comes down into the bottom-right corner of the hall. There are high windows (sill 5'-0" or more) on the north and west walls.

**Ground floor** (2,398.38 sq ft, main floor at FFL +60").
- Left column, top to bottom: **M. Bedroom** 16'-0" x 11'-0", then a **jack-and-jill toilet** 10'-3" x 5'-3" with doors to both bedrooms, then a **Bedroom** 14'-4" x 10'-5" with a corner window.
- A **5'-4" lobby** runs right from the toilet. It serves both bedroom doors and the kitchen door, and opens into the dining area. There is a cupboard (C.B.) in the pier next to the M. Bedroom door.
- Centre top: **Dining Area** 15'-9" x 16'-10" (ceiling 9'-5"). A wide arch between a pier and a column opens it to the **Drawing Area** 18'-10" x 16'-10" (ceiling 10'-11"). The bottom strip of the drawing area works as the entrance foyer.
- **Main entrance:** a double door in the south wall of the drawing area, from the entrance landing (FFL +42"). The **front porch** (ceiling 10'-6", two round columns) is in front of the drawing room window.
- Bottom row, left to right: **Kitchen** 10'-2" x 9'-9", then the **split-level stair**, then a small **Toilet** 3'-4" wide, then the **Office** 10'-4" x 9'-10" (ceiling 11'-11", corner window, side door to the covered porch).
  - The stair has a top landing at the main floor (+60") and a bottom landing at +24" with a rear door to the parking. One flight goes up to the first floor and one goes down to the basement.
- Right of the office: a **covered porch** (ceiling 8'-3") with two pillars and an **external spiral stair** up to the first-floor rear balcony.

**First floor** (2,117.72 sq ft). It sits over the ground floor, shifted so its left wall lines up.
- A **3'-6" balcony** runs the full depth of the north (left) side. Both left bedrooms open onto it.
- Left column: **Bedroom 1** 17'-0" x 11'-1", a **jack-and-jill toilet** 10'-7.5" x 5'-8", and **Bedroom 2** 17'-0" x 13'-10" (it has a bay or window seat on the balcony side).
- A short **lobby** (sunk 7") opens into the **Living Area** 18'-4" x 17'-3", which is over the dining room.
- **Bedroom 3** 15'-10" x 17'-3" (over the drawing room) has a wardrobe wall, a door to the **front balcony** 6'-0" x 11'-4", an **attached toilet** 10'-4" x 10'-8" with a bathtub, and a double door to the **rear balcony** 14'-3" x 15'-6.5" (pergola, parapet 2'-6", reached by the spiral stair).
- Bottom row: **Kitchen** 8'-3" x 13'-5.5", the **stair** (up to the terrace), and the toilet with a 2'-9" utility balcony behind it.
- From the stair a door leads down 18" to a landing and an open **Terrace** 17'-9" x 16'-9", drawn over the ground-floor parking zone.

**Terrace** (330.89 sq ft built up, 2,079.54 sq ft open). This is the open roof with a **stair room** (ceiling 7'-9"), a **Pantry** 6'-10" x 5'-9" and a **Toilet** 6'-10" x 4'-3" in one block above the stair core. An **MS (steel) structure** shades the north-east part along the east parapet. A second pergola with a column is at the south-east corner.

## Vastu zoning

The 3x3 grid is laid over the whole plot (82'-5" x 47'). With that grid the
small ground floor toilet by the stair and the first floor tub bathroom both
fall in the centre zone, which is what you saw. The zone names assume drawing
up = East. The compass on the sheets is turned about 24 degrees, so each zone
name is approximate. `design_v1.html` lists the zone of every WC, stair, lift,
hob and entrance on each floor.

## Things I marked as uncertain

1. **Your hand marks on the ground floor.** These are kept as `annotations`, not as building elements:
   - a green sketch that looks like a U-shaped sofa against the top wall of the Drawing Area (`gf.a.sofa_sketch`);
   - yellow scribbles over the office's top wall (`gf.a.yellow_office_top`) and bottom wall (`gf.a.yellow_office_bottom`).

   I have not acted on them. Tell me what they mean (for example, remove those walls).
2. Two values can't be read on the PDF: the office side-door lintel and the small ground floor toilet (`9'-?`). They are marked "illegible".
3. The terrace sheet is less precise than the others (see Accuracy above).
4. Door swing directions come from the arcs on the drawing. The hinge side is not always clear.
