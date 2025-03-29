# Taken from OpenCV documentation
# NOTE: may restrict
VALID_IMAGE_EXTS = (
    "bmp",
    "dib",
    "jpeg",
    "jpg",
    "jpe",
    "jp2",
    "png",
    "webp",
    "avif",
    "pbm",
    "pgm",
    "ppm",
    "pxm",
    "pnm",
    "pfm",
    "sr",
    "ras",
    "tiff",
    "tif",
    "exr",
    "hdr",
    "pic",
)


def colors_to_str(colors: list[tuple[int, int, int]]) -> str:
    color_str = ""
    for blue, green, red in colors:
        color_str += f"{blue:03d}{green:03d}{red:03d}"
    return color_str


def str_to_colors(color_str: str) -> list[tuple[int, int, int]]:
    colors = []
    for idx in range(0, len(color_str), 9):
        blue_str = color_str[idx : idx + 3]
        green_str = color_str[idx + 3 : idx + 6]
        red_str = color_str[idx + 6 : idx + 9]
        colors.append((int(blue_str), int(green_str), int(red_str)))
    return colors
