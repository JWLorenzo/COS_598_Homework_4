# GameMap class
# Not much going on here. Builds the map cell by cell
# with a random terrain type.

import random
import vec2
import cell
import params

class GameMap:
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.cells = {}
        for x in range(width):
            for y in range(height):
                self.cells[vec2.Vec2(x, y)] = cell.Cell(
                    params.get_random_terrain(random.random()))

    def get_cell(self, pos):
        return self.cells[pos]
