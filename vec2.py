# A simple vector 2 class to track unit and city positions.
#
# NOTE: You can make use of the distance_line and distance_man
# functions in your AI code.

import math


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, o):
        return o.x == self.x and o.y == self.y

    def __ne__(self, o):
        return not (self == o)

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f"({self.x},{self.y})"

    def __add__(self, o):
        return Vec2(self.x + o.x, self.y + o.y)

    # Straight-line distance
    def distance_line(self, o):
        return math.sqrt((o.x - self.x) ** 2 + (o.y - self.y) ** 2)

    # Manhattan distance
    def distance_man(self, o):
        return (o.x - self.x) + (o.y - self.y)

    def mod(self, map_width, map_height):

        self.y = (self.y + map_height) % map_height
        if self.y % 2 == 0:
            num_cols = map_width + 1
            col = (self.x // 2 + num_cols) % num_cols
            self.x = col * 2

        else:
            num_cols = map_width
            col = ((self.x - 1) // 2 + num_cols) % num_cols
            self.x = col * 2 + 1
        # self.x = (self.x + maxX) % maxX
        # self.y = (self.y + maxY) % maxY
        print(f"mod: {self.x}, {self.y}")


MOVES = {
    "E": Vec2(2, 0),
    "NE": Vec2(1, -1),
    "NW": Vec2(-1, -1),
    "SE": Vec2(1, 1),
    "SW": Vec2(-1, 1),
    "W": Vec2(-2, 0),
}
