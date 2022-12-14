import numpy as np
from PIL import Image
import pathlib, os

tiles_directory = (
    pathlib.Path(__file__) / ".." / ".." / "assets" / "sprites" / "tiles"
).resolve()

tiles_names = [
    "tile_00",
    "tile_01",
    "tile_02",
    "tile_03",
    "tile_04",
    "tile_12",
    "tile_23",
    "tile_34",
    "tile_14",
    "tile_13",
    "tile_24",
    "tile_15",
    "tile_25",
    "tile_35",
    "tile_45",
]
tile_ext = ".png"

original_color = [
    "white",
    (255, 255, 255),
]

new_colors = {
    "silver": (192, 192, 192),
    "gray": (128, 128, 128),
    "red": (255, 0, 0),
    "orange": (255, 165, 0),
    "moccasin": (255, 228, 181),
    "green": (0, 128, 0),
    "lime": (0, 255, 0),
    "yellow": (255, 255, 0),
    "purple": (128, 0, 128),
    "magenta": (255, 0, 255),
    "navy": (0, 0, 128),
    "blue": (0, 0, 255),
    "teal": (0, 128, 128),
    "cyan": (0, 255, 255),
    "maroon": (128, 0, 0),
}

for tile_name in tiles_names:
    for color_name, color in new_colors.items():
        tile_file = tile_name + "_" + original_color[0] + tile_ext
        im = Image.open(tiles_directory / original_color[0] / tile_file)
        data = np.array(im)
        r1, g1, b1 = original_color[1]
        r2, g2, b2 = color
        red, green, blue = data[:, :, 0], data[:, :, 1], data[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data[:, :, :3][mask] = [r2, g2, b2]
        im = Image.fromarray(data)
        new_tile_file = tile_name + "_" + color_name + tile_ext

        if not os.path.exists(tiles_directory / color_name):
            os.makedirs(tiles_directory / color_name)

        im.save(
            tiles_directory / color_name / new_tile_file,
        )
