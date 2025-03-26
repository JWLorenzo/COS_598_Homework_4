# Cell Class
# Stores the attack/defense modifiers and the color
# for each terrain type. Terrain types are defined in
# cell_terrain.py
#
# Currently, Open terrain gives a +2 for an attacker and
# nothing to a defender. Forest gives a +2 to the defender
# and nothing to the attacker.
#
# Feel free to modify.


import cell_terrain


class Cell:
    def __init__(self, terrain):
        self.terrain = terrain

    # TODO: replace this with a data member instead
    # of a function.
    def get_color(self):
        match self.terrain:
            case cell_terrain.Terrain.Open:
                return "olivedrab2"
            case cell_terrain.Terrain.Forest:
                return "springgreen4"

    def get_attack_mod(self):
        match self.terrain:
            case cell_terrain.Terrain.Open:
                return 2
            case cell_terrain.Terrain.Forest:
                return 0

    def get_defense_mod(self):
        match self.terrain:
            case cell_terrain.Terrain.Open:
                return 0
            case cell_terrain.Terrain.Forest:
                return 2
