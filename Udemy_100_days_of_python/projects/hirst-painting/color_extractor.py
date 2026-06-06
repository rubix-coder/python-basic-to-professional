import colorgram


def extract(file, colours):
    colors = colorgram.extract(file, colours)
    color_list = []
    for color in colors:
        r = color.rgb.r
        g = color.rgb.g
        b = color.rgb.b
        color_list.append((r, g, b))
    return color_list
