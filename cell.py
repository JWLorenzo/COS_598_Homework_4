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
        self.influences = [[0, 0], [0, 0], [0, 0]]

    def get_color(self):
        match self.terrain:
            case cell_terrain.Terrain.Field:
                return "olivedrab2"
            case cell_terrain.Terrain.Forest:
                return "springgreen4"
            case cell_terrain.Terrain.Desert:
                return "khaki"
            case cell_terrain.Terrain.Hill:
                return "sienna4"
            case cell_terrain.Terrain.Mountain:
                return "gray"
            case cell_terrain.Terrain.Pasture:
                return "green"

    def get_attack_mod(self):
        match self.terrain:
            case cell_terrain.Terrain.Field:
                return 2
            case cell_terrain.Terrain.Forest:
                return 0
            case cell_terrain.Terrain.Desert:
                return 2
            case cell_terrain.Terrain.Hill:
                return 1
            case cell_terrain.Terrain.Mountain:
                return 0
            case cell_terrain.Terrain.Pasture:
                return 1

    def get_defense_mod(self):
        match self.terrain:
            case cell_terrain.Terrain.Field:
                return 0
            case cell_terrain.Terrain.Forest:
                return 2
            case cell_terrain.Terrain.Desert:
                return 0
            case cell_terrain.Terrain.Hill:
                return 1
            case cell_terrain.Terrain.Mountain:
                return 2
            case cell_terrain.Terrain.Pasture:
                return 1

    def get_terrain_penalty(self):
        match self.terrain:
            case cell_terrain.Terrain.Field:
                return 2
            case cell_terrain.Terrain.Forest:
                return 3
            case cell_terrain.Terrain.Desert:
                return 4
            case cell_terrain.Terrain.Hill:
                return 3
            case cell_terrain.Terrain.Mountain:
                return 5
            case cell_terrain.Terrain.Pasture:
                return 2

    def get_influence(self, faction_id, influence_type):
        if faction_id == "Red":
            return self.influences[influence_type][0]
        elif faction_id == "Blue":
            return self.influences[influence_type][1]
