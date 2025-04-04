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
        for y in range(height):
            if y % 2 == 0:
                for x in range(0, (width * 2) + 1, 2):
                    self.cells[vec2.Vec2(x, y)] = cell.Cell(
                        params.get_random_terrain(random.random())
                    )
                    print(f"Even Cell {x},{y}: {self.cells[vec2.Vec2(x, y)]}")
            else:
                for x in range(1, (width * 2) + 1, 2):
                    self.cells[vec2.Vec2(x, y)] = cell.Cell(
                        params.get_random_terrain(random.random())
                    )
                    print(f"Odd Cell {x},{y}: {self.cells[vec2.Vec2(x, y)]}")
            if x == 15 and y == 2:
                print("huh")
                exit()

    def get_cell(self, pos):
        print(f"Getting cell {pos}")
        return self.cells[pos]
