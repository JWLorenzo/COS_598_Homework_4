# AI Class
# by zax

# This is the main file you will edit. The run_ai function's job
# is to issue two types of commands (see command.py):
# - BuildUnitCommand: asks the game engine to build a specific type
#     of unit at a specific city if the faction has enough cash
#     available.
# - MoveUnitCommand: asks the game engine to move a specific unit
#     in a specific direction. The engine will only move a unit
#     if the destination cell is free. If it is occupied by a friendly
#     unit, nothing happens. If it is occupied by another faction,
#     combat ensues.

from command import *
import random
import unit
from pathfinding import reconstruct_path, a_star


class AI:
    # init:
    # Currently, the initializer adds nothing to the object.
    # You are welcome to modify to have a place to keep
    # information that persists across calls to run_ai().
    #
    # NOTE: AI objects are passed into the Faction initializer
    # when a faction is created (see the gen_factions() function
    # in the main.py file). If you'd like to subclass the AI class
    # to differentiate between faction behaviors, you are welcome
    # to do so.
    def __init__(self):
        pass

    # run_ai
    # Parameters:
    # - faction_id: this is the faction_id of this AI object.
    #     Use it to access infomation in the other parameters.
    # - factions: dictionary of factions by faction_id.
    # - cities: dictionary of cities stored by faction_id.
    #     For example: cities[faction_id] would return all the
    #     the city objects owned by this faction.
    # - units: dictionary of all units by faction_id.
    #     Similar to the cities dictionary, units[faction_id]
    #     would return all unit objects belonging to the faction.
    # - gmap: the game map object. You can use this (if you wish)
    #     to get information about the map and terrain.
    #
    # Return:
    # This function should return a list of commands to be processed
    # by the game engine this turn.
    #
    # NOTE: You should replace the following code with your
    # own. The code currently gives the factions totally random
    # behavior. Totally random behavior, while interesting,
    # is not an acceptable solution.
    #
    # NOTE 2: Every ai has access to ALL game objects. This means
    # you can (and should) access the unit and city locations
    # of the other faction. I STRONGLY advise against manually
    # changing unit or city locations from the AI file. Doing so
    # circumvents checks made by the game engine and is likely to
    # have bad side effects. If you want something more actions
    # than those provided by the two commands, I suggest taking
    # the time to create additional Command subclasses and properly
    # implement them in the engine (main.py).

    def run_ai(self, faction_id, factions, cities, units, gmap, unit_dict):
        cmds = []
        magic_number = 5
        if faction_id == "Red":
            positions = [x[1] for x in gmap.highest["Blue"] if x[0] > magic_number]
            weights = [
                x[0]
                + (
                    gmap.get_cell(x[1]).get_attack_mod()
                    + gmap.get_cell(x[1]).get_defense_mod()
                )
                + (
                    gmap.get_cell(x[1]).influences[1][0]
                    + gmap.get_cell(x[1]).influences[2][0]
                )
                for x in gmap.highest["Blue"]
                if x[0] > magic_number
            ]
            unit_weights = [
                gmap.economy["Blue"]["S"] + 1,
                gmap.economy["Blue"]["P"] + 1,
                gmap.economy["Blue"]["R"] + 1,
            ]
            unit_counts = [
                gmap.economy["Blue"]["S"],
                gmap.economy["Blue"]["P"],
                gmap.economy["Blue"]["R"],
            ]
            threat_list = [x[0] for x in gmap.threats["Blue"]]
            threat_weights = [x[1] for x in gmap.threats["Blue"]]

        else:
            positions = [x[1] for x in gmap.highest["Red"] if x[0] > magic_number]
            weights = [
                x[0]
                + (
                    gmap.get_cell(x[1]).get_attack_mod()
                    + gmap.get_cell(x[1]).get_defense_mod()
                )
                + (
                    gmap.get_cell(x[1]).influences[1][1]
                    + gmap.get_cell(x[1]).influences[2][1]
                )
                for x in gmap.highest["Red"]
                if x[0] > magic_number
            ]
            unit_weights = [
                gmap.economy["Red"]["S"] + 1,
                gmap.economy["Red"]["P"] + 1,
                gmap.economy["Red"]["R"] + 1,
            ]
            unit_counts = [
                gmap.economy["Red"]["S"],
                gmap.economy["Red"]["P"],
                gmap.economy["Red"]["R"],
            ]
            threat_list = [x[0] for x in gmap.threats["Red"]]
            threat_weights = [x[1] for x in gmap.threats["Red"]]
        # Unit Builing

        my_cities = cities[faction_id]
        city_indexes = list(range(len(my_cities)))
        random.shuffle(city_indexes)
        for ci in city_indexes:

            unit_choice = random.choices(["R", "S", "P"], weights=unit_weights, k=1)[0]
            cmd = BuildUnitCommand(faction_id, my_cities[ci].ID, unit_choice)
            cmds.append(cmd)

        # Pathfinding for units

        if (
            sum(unit_counts)
            >= sum(
                [
                    gmap.economy[faction_id]["S"],
                    gmap.economy[faction_id]["P"],
                    gmap.economy[faction_id]["R"],
                ]
            )
            and len(threat_list) > 0
        ):
            my_units = units[faction_id]
            for u in my_units:
                chosen_tile = random.choices(threat_list, weights=threat_weights, k=1)[
                    0
                ]
                came_from, cost_so_far = a_star(
                    u.pos, chosen_tile, gmap, unit_dict, u.faction_id
                )
                u.queue = reconstruct_path(came_from, u.pos, chosen_tile)
                if len(u.queue) > 0:
                    move_dir = u.queue[-1][1]
                else:
                    move_dir = random.choice(list(vec2.MOVES.keys()))

                cmds.append(MoveUnitCommand(faction_id, u.ID, move_dir))
        else:
            # Attack Behavior
            my_units = units[faction_id]
            for u in my_units:
                if len(u.queue) > 0 and u.queue[-1][0] == u.pos:
                    u.queue.pop()

                if not (len(u.queue) == 0):
                    next_pos = u.pos + vec2.MOVES[u.queue[-1][1]]
                    next_pos.mod(gmap.width, gmap.height)
                    if (
                        next_pos in unit_dict.by_pos
                        and unit_dict.by_pos[next_pos].faction_id == faction_id
                    ):
                        u.queue.clear()
                        rand_dir = random.choice(list(vec2.MOVES.keys()))
                        cmds.append(MoveUnitCommand(faction_id, u.ID, rand_dir))
                        continue

                if len(u.queue) == 0:

                    chosen_tile = random.choices(positions, weights=weights, k=1)[0]

                    came_from, cost_so_far = a_star(
                        u.pos, chosen_tile, gmap, unit_dict, u.faction_id
                    )
                    u.queue = reconstruct_path(came_from, u.pos, chosen_tile)
                if len(u.queue) > 0:
                    move_dir = u.queue[-1][1]
                else:
                    move_dir = random.choice(list(vec2.MOVES.keys()))

                cmds.append(MoveUnitCommand(faction_id, u.ID, move_dir))

        return cmds
