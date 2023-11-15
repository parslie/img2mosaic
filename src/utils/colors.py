import numpy


def clamp_color(color: numpy.ndarray, complexity: int) -> numpy.ndarray:
    color = color.copy()
    color[0] -= color[0] % complexity
    color[1] -= color[1] % complexity
    color[2] -= color[2] % complexity
    return color


def colors_to_key(colors: list[numpy.ndarray]) -> str:
    key = ''
    for color in colors:
        key += f'{color[0]} {color[1]} {color[2]} '
    return key[:-1]


def key_to_colors(key: str) -> list[numpy.ndarray]:
    colors = []

    key_split = key.split(' ')
    for i in range(0, len(key_split), 3):
        color = numpy.array([int(x) for x in key_split[i:i+3]], dtype=numpy.uint8)
        colors.append(color)
    
    return colors


def color_sqr_dist(color_1: numpy.ndarray, color_2: numpy.ndarray) -> float:
    diff_b = int(color_1[0]) - int(color_2[0])
    diff_g = int(color_1[1]) - int(color_2[1])
    diff_r = int(color_1[2]) - int(color_2[2])
    return diff_b ** 2 + diff_g ** 2 + diff_r ** 2


def colors_to_closest_key(palette: dict, colors: list[numpy.ndarray]) -> str:
    closest_sqr_dist = float('inf')
    closest_key = None

    for close_key in palette.keys():
        close_colors = key_to_colors(close_key)

        sqr_dist = 0
        for i in range(len(close_colors)):
            # Each color list should be the same size
            sqr_dist += color_sqr_dist(colors[i], close_colors[i])

        if sqr_dist < closest_sqr_dist:
            closest_sqr_dist = sqr_dist
            closest_key = close_key

    return closest_key
