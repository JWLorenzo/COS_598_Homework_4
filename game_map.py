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
        self.highest = {"Red": [], "Blue": []}
        self.economy = {
            "Red": {"R": 0, "S": 0, "P": 0},
            "Blue": {"R": 0, "S": 0, "P": 0},
        }

        for y in range(height):
            if y % 2 == 0:
                for x in range(0, width * 2, 2):
                    self.cells[vec2.Vec2(x, y)] = cell.Cell(
                        params.get_random_terrain(random.random())
                    )
                    self.cells[vec2.Vec2(x, y)].cost = self.get_cell(
                        vec2.Vec2(x, y)
                    ).get_terrain_penalty()
            else:
                for x in range(1, width * 2, 2):
                    self.cells[vec2.Vec2(x, y)] = cell.Cell(
                        params.get_random_terrain(random.random())
                    )
                    self.cells[vec2.Vec2(x, y)].cost = self.get_cell(
                        vec2.Vec2(x, y)
                    ).get_terrain_penalty()

    def get_cell(self, pos):
        return self.cells[pos]
