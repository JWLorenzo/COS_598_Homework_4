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
        # for x in range(width):
        #     for y in range(height):
        #         self.cells[vec2.Vec2(x, y)] = cell.Cell(
        #             params.get_random_terrain(random.random())
        #         )

        list_tester = []
        for y in range(height):
            some_list = []
            if y % 2 == 0:
                for x in range(0, width * 2, 2):
                    some_list.append((x, y))
                    self.cells[vec2.Vec2(x, y)] = cell.Cell(
                        params.get_random_terrain(random.random())
                    )
            else:
                some_list.append(())
                for x in range(1, width * 2, 2):
                    some_list.append((x, y))
                    self.cells[vec2.Vec2(x, y)] = cell.Cell(
                        params.get_random_terrain(random.random())
                    )
                # self.cells[vec2.Vec2(x, y)] = cell.Cell(
                #     params.get_random_terrain(random.random()))
            list_tester.append(some_list)
        for i in list_tester:
            print("List tester:", i)
        # exit(0)

    def get_cell(self, pos):
        return self.cells[pos]
