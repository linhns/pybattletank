# Creating Levels

## Requirements

- Download and install [Tiled](https://thorbjorn.itch.io/tiled)
- Retrieve tilesets from [here](https://github.com/linhns/pybattletank/tree/main/pybattletank/assets).
  Put **ground.png**, **walls.png**, **units.png**, **explosions.png** into
  a folder.

![Tiled](./assets/images/tiled.png)

## Procedure

### Create a map

1. Launch Tiled.
2. From the menu bar, select **File > New > New Map...**.
3. In the *Map* section, set *Orientation* to **Orthogonal**.
4. In the *Map size* section, select **Fixed** and enter the width and height of
   your level.
5. In the *Tile size* section, set both tile width and height to **64 px**.
6. Select **File > Save as...** from the menu bar and save the level in the same
   folder as the tilesets.

### Adding layers

1. In the *Layers* tab on the right sidebar, use the first icon to add a new
   layer. Select **Tile layer**.
2. Double-click on the created layer to rename it. Name it **Ground**.
3. Repeat for **Walls**, **Tanks**, **Towers** and **Explosions** in this order.

### Adding tilesets

1. In the *Tilesets* tab on the right sidebar, use the first icon to add a new
   layer.
2. Browse and select the **ground.png** file downloaded above.
3. Check **Embed in map** and click OK.
4. Repeat for other tilesets.

### Editing the level

1. Left-click on a layer to select it.
2. Select a tileset and choose a tile from that set.
3. Make sure the *Stamp Brush* tool is selected from the top bar.
4. Stamp this tile on the map to start drawing.

!!! note

    Only use tiles from a single tileset per layer, otherwise the level cannot
    be loaded.

For the **Tanks** layer, put a single tank tile to indicate the starting
position of the player.

For the **Explosions** layer, put a single tile from the explosion tileset.
