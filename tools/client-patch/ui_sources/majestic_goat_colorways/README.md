# Costume Majestic Goat colorways

This asset set clones the master costume item `19549` (`C_Magestic_Goat`) and
replaces only the curled horn's eight-color palette ramp. The existing gold
center ornament, outlines, shape, and ACT animation remain from the master.

The inventory icon comes from the official 24x24 bitmap for item `400124`
(`Costume Majestic Goat of Dawn`). Its source pixel placement is preserved and
only the eight horn-ramp palette entries are recolored. Magenta transparency is
normalized to palette index 0. The 75x100 collection preview also comes from
item `400124`; only its pink horn surface is selected for recoloring. The gold
ornament, warm side/ear tips, cast shadow, pixel placement, and per-pixel
pixel layout remain from the source. Source brightness maps continuously onto
the target tone ramp to keep gray and black finishes distinct. Equipped
accessory sprites keep the original master item's placement.

The fifteen color entries include two new comparisons for Archangel Wings
item `2573`: `Archangel Match` (`902288`) samples its inventory-icon shades and
`Warm Feather` (`902289`) keeps the white warm with softer taupe shadows. The
gold center ornament and warm ear tips remain intact. Existing color entries
and IDs `902275` through `902287` remain available for comparison.
The original brown master item remains item `19549`; no gold recolor is included.

`build_majestic_goat_colorways.py` reads the equipped sprites from the master
item in `Client-master-pc/data.grf`, both preview images from item `400124`, and
the current custom accessory tables from
`Client-master-pc/midnight.grf`. The first build saves the source LUB and itemInfo snapshots
here so later builds can safely replace this batch without duplicating mappings.
`colorways_contact_sheet.png` and per-color preview images show the recolored
sprites. `collection_recolor_mask.png` shows the collection image area changed.

IDs, names, resources, View IDs, and color ramps are recorded in
`colorways.json` and in the builder source.
