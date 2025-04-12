import random
import copy
import pygame
import pygame.freetype
import game_map
import params
import faction
import ai
import city
import vec2
import unit
import command
import cell_terrain
import os
import math
import argparse
from queue import PriorityQueue
from typing import Optional

MAP_WIDTH = 30
MAP_HEIGHT = 20
CELL_SIZE = 32
TEXT_SIZE = 20
SCALE = 1.75
DEBUG_MODE = True


# ###################################################################
# DISPLAY
# The display part of the engine. Unless you want to mess with
# the look and feel (add sprites or something) you probably don't need
# to mess with anything in this section
# ####################################################################
class Display:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.run = True
        self.delta = 0
        self.font = None
        self.map_cell_size = CELL_SIZE

    # fmt: off
    def draw_gobj(self, gobj):
        pygame.draw.circle(
            self.screen,
            gobj.color,
            gobj.pos(),
            gobj.radius)
        
    def pointy_hex_corner(self,center:tuple, size:int, i:int) -> tuple:
        angle_deg = 60 * i - 30
        angle_rad = math.pi / 180 * angle_deg
        return (center[0] + size * math.cos(angle_rad),
                    center[1] + size * math.sin(angle_rad))

    def draw_text(self, msg, x, y, color,scale=(1,1),):
        surface, rect = self.font.render(msg, color)
        surface = pygame.transform.scale(surface, (int(rect.width*scale[0]), int(rect.height*scale[1])))
        self.screen.blit(surface, (x, y))

    def draw_line(self, p1, p2, color, width=1):
        pygame.draw.line(
            self.screen,
            color,
            p1,
            p2,
            width)

    def draw_map(self, gmap,background):
        terrain_images = {}
        cell_x= self.map_cell_size*math.sqrt(3)
        cell_y= self.map_cell_size *2
        for terrain in cell_terrain.Terrain.__members__.keys():
            image = pygame.image.load(os.path.join(os.getcwd(),"Tile_Images",terrain.lower()+".png"))
            image = pygame.transform.scale(image,(cell_x,cell_y))
            terrain_images[terrain] = image

        for v, c in gmap.cells.items():
            # pygame.draw.rect(
            #     self.screen,
            #     c.get_color(),
            #     pygame.rect.Rect(
            #         v.x*self.map_cell_size,
            #         v.y*self.map_cell_size,
            #         self.map_cell_size,
            #         self.map_cell_size),
            #     width=0)
            points = []
            rect = terrain_images[c.terrain.name].get_rect()
            rect = rect.move(v.x*self.map_cell_size*math.sqrt(3)/2 ,v.y*cell_y*.75)
            background.blit(terrain_images[c.terrain.name],rect )
            for i in range(1,7):
                x_coord = (v.x*self.map_cell_size*math.sqrt(3)/2 + self.map_cell_size*math.sqrt(3)/2)  
                y_coord = (v.y * self.map_cell_size * 3/4*2 + self.map_cell_size)
                side_size = self.map_cell_size
                points.append(self.pointy_hex_corner( (x_coord,y_coord),side_size, i))

            draw_polygon(background,points, "tan", width=3)

    def draw_cities(self, cities, factions):
        for c in cities:
            f = factions[c.faction_id]
            points = []
            for i in range(1,7):
                x_coord = (c.pos.x*self.map_cell_size*math.sqrt(3)/2 + self.map_cell_size*math.sqrt(3)/2)
                y_coord = (c.pos.y*self.map_cell_size* 3/4*2 + self.map_cell_size)
                side_size = self.map_cell_size
                points.append(self.pointy_hex_corner( (x_coord,y_coord),side_size, i))

            draw_polygon(self.screen,points, f.color)
            # pygame.draw.rect(
            #     self.screen,
            #     f.color,
            #     pygame.rect.Rect(
            #         c.pos.x*self.map_cell_size*.5,
            #         c.pos.y*self.map_cell_size*.75,
            #         self.map_cell_size,
            #         self.map_cell_size
            #     ),
            #     width=2
            # )
            if args.verbose:
                self.draw_text(
                        f"({c.pos.x},{c.pos.y})",
                        (c.pos.x*self.map_cell_size*math.sqrt(3)/2+self.map_cell_size*math.sqrt(3)/2), 
                        (c.pos.y*self.map_cell_size* 3/4*2 +self.map_cell_size),
                        "black")
    def draw_units(self, unit_dict, factions):
        padding = 5
        for fid, ulist in unit_dict.by_faction.items():
            fcolor = factions[fid].color
            for u in ulist:
                msg  = u.utype
                if args.verbose:
                    msg = f"({u.pos.x},{u.pos.y}){u.utype}"
                metrics = self.font.get_metrics(u.utype)[0]
                if args.verbose:
                    print(f"metrics: {metrics}")

                rect_x =(u.pos.x*self.map_cell_size*math.sqrt(3)/2+self.map_cell_size*math.sqrt(3)/2)
                rect_y =(u.pos.y*self.map_cell_size* 3/4*2 +self.map_cell_size)
                rect_width = metrics[1]-metrics[0]
                rect_height = metrics[3]-metrics[2]
                draw_rectangle(self.screen,(rect_x,rect_y,rect_width,rect_height),"white",padding)
                self.draw_text(
                    msg,
                    (u.pos.x*self.map_cell_size*math.sqrt(3)/2+self.map_cell_size*math.sqrt(3)/2),
                    (u.pos.y*self.map_cell_size* 3/4*2 +self.map_cell_size),
                    fcolor)
                
    def draw_influence(self, gmap):
        for c in gmap.cells:
            if sum(map(sum,gmap.cells[c].influences)) > 0:
                self.draw_text(
                            f"{gmap.cells[c].influences[0]},{gmap.cells[c].influences[1]},{gmap.cells[c].influences[2]}",
                            (c.x*self.map_cell_size*math.sqrt(3)/2), 
                            (c.y*self.map_cell_size* 3/4*2 +self.map_cell_size),
                            "black",scale=(.7,.7))


def draw_rectangle(
    screen: pygame.display,
    xywh: tuple,
    color: pygame.color,
    padding: int,
    width: int = 0,
):
    pygame.draw.rect(
        screen,
        color,
        (
            xywh[0] - padding,
            xywh[1] - padding,
            xywh[2] + padding * 2,
            xywh[3] + padding * 2,
        ),
        width,
    )


def draw_polygon(screen, points: list, color: pygame.color, width=3):
    pygame.draw.polygon(screen, color, points, width)


def init_display(text_modifier: int = 1):
    pygame.init()
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h))
    clock = pygame.time.Clock()
    display = Display(screen, clock)
    display.font = pygame.freetype.Font("JuliaMono-Bold.ttf", text_modifier * TEXT_SIZE)
    pygame.key.set_repeat(200, 100)
    return display


# ###############################################################
# GAME GENERATION FUCNTIONS
# This section generates the map, factions and cities.
# If you add things to the game (additional terrain, factions,
# city types, etc), you'll need to edit these functions to have
# them placed on the map
# ###############################################################
def gen_game_map(width, height):
    return game_map.GameMap(width, height)


def gen_factions(gmap):

    factions = {}
    factions["Red"] = faction.Faction(
        "Red", params.STARTING_FACTION_MONEY, ai.AI(), "red"
    )
    factions["Blue"] = faction.Faction(
        "Blue", params.STARTING_FACTION_MONEY, ai.AI(), "blue"
    )

    return factions


def gen_cities(gmap, faction_ids):
    city_positions = []
    cities = []
    faction_id_index = 0

    for i in range(params.CITIES_PER_FACTION * len(faction_ids)):

        # A new red city
        new_city_pos = None
        while True:
            new_city_y = random.randrange(gmap.height)

            if new_city_y % 2 == 0:

                new_city_x = random.randrange(0, gmap.width * 2, 2)
            else:
                new_city_x = random.randrange(1, gmap.width * 2, 2)

            new_city_pos = vec2.Vec2(new_city_x, new_city_y)
            if new_city_pos not in city_positions:
                city_positions.append(new_city_pos)
                break
        fid = faction_ids[faction_id_index]
        faction_id_index = (faction_id_index + 1) % len(faction_ids)

        c = city.City(
            params.get_random_city_ID(), new_city_pos, fid, params.CITY_INCOME
        )

        cities.append(c)

    return cities


# ###########################################################
# GAME ENGINE CODE
# See specific function comments below
# ##########################################################


# FactionPreTurn:
# You don't need to edit this unless you make city resources
# more complex.
# - awards each faction its income from the cities
# - stores cities in the city dictionary passed onto the AI.
def FactionPreTurn(cities, faction):

    faction_cities = []

    # #####################################################
    # FACTION DATA

    # Award income
    for c in cities:
        if c.faction_id == faction.ID:
            income = c.generate_income()
            faction.money += income

    # #####################################################
    # CITY DATA
    for c in cities:
        if c.faction_id == faction.ID:
            faction_cities.append(c)

    return faction_cities


# Turn:
# The actual turn taking function. Calls each faction's ai
# Gathers all the commands in a giant list and returns it.
def Turn(factions, gmap, cities_by_faction, units_by_faction):

    commands = []

    for fid, f in factions.items():

        cmds = f.run_ai(factions, cities_by_faction, units_by_faction, gmap)
        commands += cmds

    return commands


# RunAllCommands:
# Executes all commands from the current turn.
# Shuffles the commands to reduce P1 bias (maybe).
# Basically this is just a dispatch function.
def RunAllCommands(commands, factions, unit_dict, cities, gmap):
    random.shuffle(commands)
    move_list = []
    for cmd in commands:
        if isinstance(cmd, command.MoveUnitCommand):
            RunMoveCommand(cmd, factions, unit_dict, cities, gmap, move_list)
        elif isinstance(cmd, command.BuildUnitCommand):
            RunBuildCommand(cmd, factions, unit_dict, cities, gmap)
        else:
            print(f"Bad command type: {type(cmd)}")


# RunMoveCommand:
# The function that handles MoveUnitCommands.
def RunMoveCommand(cmd, factions, unit_dict, cities, gmap, move_list):

    if (cmd.unit_id, cmd.faction_id) in move_list:
        return
    else:
        move_list.append((cmd.unit_id, cmd.faction_id))

    # Find the unit
    ulist = unit_dict.by_faction[cmd.faction_id]
    theunit = None
    for u in ulist:
        if u.ID == cmd.unit_id:
            theunit = u
            break

    # Unit might have died before it's command could be run.
    if theunit is None:
        return

    # Get new position
    delta = vec2.Vec2(0, 0)
    try:
        delta = vec2.MOVES[cmd.direction]
    except KeyError:
        print(f"{cmd.direction} is not a valid direction")
        return

    new_pos = theunit.pos + delta

    # Modulo the new pos to the map size
    new_pos.mod(gmap.width, gmap.height)

    # Check if new_pos is free.
    move_successful = False
    if unit_dict.is_pos_free(new_pos):
        old_pos = theunit.pos
        theunit.pos = new_pos
        unit_dict.move_unit(u, old_pos, new_pos)
        move_successful = True
    # Occupied by a unit
    else:
        other_unit = unit_dict.by_pos[new_pos]

        # Is the other unit an enemy?
        if other_unit.faction_id != theunit.faction_id:
            space_now_free = RunCombat(
                theunit, other_unit, cmd, factions, unit_dict, cities, gmap
            )
            # Perhaps combat freed the space.
            # if so, move.
            if space_now_free:
                old_pos = theunit.pos
                theunit.pos = new_pos
                unit_dict.move_unit(u, old_pos, new_pos)
                move_successful = True

    # Check if the move conquerored a city
    if move_successful:
        for c in cities:
            if new_pos == c.pos:
                c.faction_id = u.faction_id
                break


# RunBuildCommand:
# Executes the BuildUnitCommand.
def RunBuildCommand(cmd, factions, unit_dict, cities, gmap):
    # How much does the unit cost?
    f = factions[cmd.faction_id]
    cost = unit.get_unit_cost(cmd.utype)

    # Does the faction have the available resources (money)?
    if f.can_build_unit(cost):

        # Look for the city
        for c in cities:
            if c.ID == cmd.city_id:

                # If there's no unit in the city, build.
                # Add to the unit dictionary and charge
                # the faction for its purchase.
                if unit_dict.is_pos_free(c.pos):

                    uid = f.get_next_unit_id()
                    new_unit = unit.Unit(
                        uid,
                        cmd.utype,
                        f.ID,
                        copy.copy(c.pos),
                        unit.UNIT_HEALTH[cmd.utype],
                        0,
                    )
                    unit_dict.add_unit(new_unit)

                    f.money -= cost


# RunCombat:
# Called by the MoveUnitCommand if a unit tries to move into a cell
# containing a unit of the opposing faction.
#
# Combat is mutually destructive in that both units damage each other.
# and can both die. You are welcome to edit this if you want combat
# to work differently.
#
# Returns whether the defender was destroyed (and the attacker not)
# allowing the attacker to move into the cell.
def RunCombat(attacker, defender, cmd, factions, unit_dict, cities, gmap):
    # Find the terrain each unit stands in.
    att_cell = gmap.get_cell(attacker.pos)
    def_cell = gmap.get_cell(defender.pos)

    # Make the combat rolls.
    att_roll = attacker.roll(defender.utype)
    def_roll = defender.roll(attacker.utype)

    # Add terrain modifiers.
    att_roll += att_cell.get_attack_mod()
    def_roll += def_cell.get_defense_mod()

    # Damage health.
    defender.health -= att_roll
    attacker.health -= def_roll

    # Debug output
    # print(f"Combat - {attacker.faction_id}: {att_roll} v {defender.faction_id}: {def_roll}")

    # Did anyone die? If the defender died and the attacker
    # did not, return that the attacker is free to move into
    # the cell.
    can_move = False
    if defender.health <= 0:
        # print(f"   {defender.faction_id} died")
        unit_dict.remove_unit(defender)
        can_move = True
    if attacker.health <= 0:
        # print(f"   {attacker.faction_id} died")
        unit_dict.remove_unit(attacker)
        can_move = False

    return can_move


# ###########################################################
# THE UNIT DICTIONARY
# Modify at your own risk. Probably no need.
# ###########################################################
class UnitDict:
    def __init__(self, faction_ids):
        self.by_pos = {}
        self.by_faction = {}
        for fid in faction_ids:
            self.by_faction[fid] = []

    def add_unit_by_pos(self, u, pos):
        if pos not in self.by_pos:
            self.by_pos[pos] = u

    def remove_unit_by_pos(self, u, pos):
        if u == self.by_pos[pos]:
            del self.by_pos[pos]

    def move_unit(self, u, old_pos, new_pos):
        self.remove_unit_by_pos(u, old_pos)
        self.add_unit_by_pos(u, new_pos)

    def add_unit(self, u):
        self.by_faction[u.faction_id].append(u)
        self.add_unit_by_pos(u, u.pos)

    def remove_unit(self, u):
        self.by_faction[u.faction_id].remove(u)
        self.remove_unit_by_pos(u, u.pos)

    def is_pos_free(self, pos):
        return pos not in self.by_pos


def CheckForGameOver(cities):
    faction_ids_with_cities = []
    for c in cities:
        if c.faction_id not in faction_ids_with_cities:
            faction_ids_with_cities.append(c.faction_id)
    return len(faction_ids_with_cities) == 1, faction_ids_with_cities[0]


# def ScaleUI(display, map_width, map_height):
#     window_width, window_height = pygame.display.get_window_size()
#     x = window_width / ((map_width + 0.5) * display.map_cell_size)
#     y = window_height / (
#         (display.map_cell_size * map_height)
#         - 2 * ((1 / 8) * display.map_cell_size)
#         - ((1 / 4) * display.map_cell_size * (map_height - 2))
#     )
#     display.scaling_factor = pygame.Vector2(
#         x,
#         y,
#     )
#     if args.verbose:
#         print(f"Window size: {window_width}x{window_height}")
#         print(f"x: {x}")
#         print(f"y: {y}")

#         print(f"Scaling factor: {display.scaling_factor}")


def doublewidth_distance(a: vec2.Vec2, b: tuple) -> int:
    dcol = abs(a.x - b[0])
    drow = abs(a.y - b[1])
    return drow + max(0, (dcol - drow) / 2)


def doublewidth_distance(a: vec2.Vec2, b: vec2.Vec2) -> int:
    dcol = abs(a.x - b.x)
    drow = abs(a.y - b.y)
    return drow + max(0, (dcol - drow) / 2)


def heuristic(start, goal):
    return doublewidth_distance(start, goal)


def get_neighbors(gmap, coord):
    neighbors = []
    for i in vec2.MOVES:
        delta = vec2.Vec2(0, 0)
        try:
            delta = vec2.MOVES[i]
        except KeyError:
            print(f"{i} is not a valid direction")
        new_pos = coord + delta

        new_pos.mod(gmap.width, gmap.height)
        neighbors.append((new_pos, i))
    return neighbors


def reconstruct_path(
    came_from: dict[vec2.Vec2, str, vec2.Vec2], start: vec2.Vec2, goal: vec2.Vec2
):
    current: list[vec2.Vec2, str] = [goal, None]
    path: list[vec2.Vec2] = []
    if goal not in came_from:
        return []
    while current[0] != start:
        path.append(current)
        current = came_from[current[0]]
    path.reverse()
    return path


# Basic A* algorithm
def a_star(start: vec2.Vec2, goal: vec2.Vec2, gmap: game_map.GameMap):
    frontier = PriorityQueue()
    frontier.put((0, (start, None)))

    came_from: dict[vec2.Vec2, str, Optional[vec2.Vec2]] = {}
    cost_so_far: dict[vec2.Vec2, float] = {}

    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        _, current = frontier.get()

        if current[0] == goal:
            break

        for next in get_neighbors(gmap, current[0]):

            new_cost = (
                cost_so_far[current[0]] + gmap.cells[next[0]].get_terrain_penalty()
            )

            if next[0] not in cost_so_far or new_cost < cost_so_far[next[0]]:
                cost_so_far[next[0]] = new_cost
                priority = new_cost + heuristic(next[0], goal)

                frontier.put((priority, (next[0], next[1])))
                came_from[next[0]] = (current[0], next[1])

    return came_from, cost_so_far


def assign_influence(
    gmap: game_map.GameMap,
    coord: vec2.Vec2,
    inf_index: int,
    fac_index: int,
    start: int,
    dist: int,
    decay: int,
) -> game_map.GameMap:
    gmap.cells[coord].influences[inf_index][fac_index] += max(0, start - dist * decay)
    return gmap


def influence_cities(
    center_coords: vec2.Vec2,
    faction_id: str,
    radius: int,
    gmap: game_map.GameMap,
    start_inf: int,
    decay: int,
    affected_dict: dict,
) -> dict:
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            tile_y = center_coords.y + dy

            if 0 <= tile_y < MAP_HEIGHT:
                tile_x = center_coords.x + dx * 2

                if tile_y % 2 == 1 and center_coords.y % 2 == 0:
                    tile_x += 1
                if tile_y % 2 == 0 and center_coords.y % 2 == 1:
                    tile_x -= 1
                if 0 <= tile_x < MAP_WIDTH * 2:
                    dist = doublewidth_distance(center_coords, (tile_x, tile_y))
                    if dist <= radius:
                        if gmap.cells.get(vec2.Vec2(tile_x, tile_y)) is not None:
                            if faction_id == "Red":
                                gmap.cells[vec2.Vec2(tile_x, tile_y)].influences[0][
                                    0
                                ] += max(0, start_inf - dist * decay)

                                gmap = assign_influence(
                                    gmap,
                                    vec2.Vec2(tile_x, tile_y),
                                    0,
                                    0,
                                    start_inf,
                                    dist,
                                    decay,
                                )
                                if (
                                    affected_dict.get(vec2.Vec2(tile_x, tile_y), None)
                                    is None
                                ):
                                    affected_dict[vec2.Vec2(tile_x, tile_y)] = ""
                            elif faction_id == "Blue":
                                gmap = assign_influence(
                                    gmap,
                                    vec2.Vec2(tile_x, tile_y),
                                    0,
                                    1,
                                    start_inf,
                                    dist,
                                    decay,
                                )

                                if (
                                    affected_dict.get(vec2.Vec2(tile_x, tile_y), None)
                                    is None
                                ):
                                    affected_dict[vec2.Vec2(tile_x, tile_y)] = ""
                        else:
                            print(
                                f"Tile ({tile_x}, {tile_y}) is out of bounds for the map."
                            )
    return affected_dict


def influence_units(
    center_coords: vec2.Vec2,
    faction_id: str,
    radius: int,
    gmap: game_map.GameMap,
    start_inf: int,
    decay: int,
    affected_dict: dict,
) -> dict:
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            tile_y = center_coords.y + dy

            if 0 <= tile_y < MAP_HEIGHT:
                tile_x = center_coords.x + dx * 2

                if tile_y % 2 == 1 and center_coords.y % 2 == 0:
                    tile_x += 1
                if tile_y % 2 == 0 and center_coords.y % 2 == 1:
                    tile_x -= 1
                if 0 <= tile_x < MAP_WIDTH * 2:
                    dist = doublewidth_distance(center_coords, (tile_x, tile_y))
                    if dist <= radius:
                        if gmap.cells.get(vec2.Vec2(tile_x, tile_y)) is not None:
                            if faction_id == "Red":

                                gmap = assign_influence(
                                    gmap,
                                    vec2.Vec2(tile_x, tile_y),
                                    1,
                                    0,
                                    start_inf,
                                    dist,
                                    decay,
                                )

                                gmap = assign_influence(
                                    gmap,
                                    vec2.Vec2(tile_x, tile_y),
                                    2,
                                    0,
                                    start_inf,
                                    dist,
                                    decay,
                                )

                                if (
                                    affected_dict.get(vec2.Vec2(tile_x, tile_y), None)
                                    is None
                                ):
                                    affected_dict[vec2.Vec2(tile_x, tile_y)] = ""

                            elif faction_id == "Blue":

                                gmap = assign_influence(
                                    gmap,
                                    vec2.Vec2(tile_x, tile_y),
                                    1,
                                    1,
                                    start_inf,
                                    dist,
                                    decay,
                                )

                                gmap = assign_influence(
                                    gmap,
                                    vec2.Vec2(tile_x, tile_y),
                                    2,
                                    1,
                                    start_inf,
                                    dist,
                                    decay,
                                )

                                if (
                                    affected_dict.get(vec2.Vec2(tile_x, tile_y), None)
                                    is None
                                ):
                                    affected_dict[vec2.Vec2(tile_x, tile_y)] = ""
                        else:
                            print(
                                f"Tile ({tile_x}, {tile_y}) is out of bounds for the map."
                            )
    return affected_dict


def influenced_tiles_cities(
    gmap: game_map.GameMap,
    units: list,
    radius: int,
    decay: int,
    start_inf: int,
    affected_dict: dict,
) -> dict:
    # to prevent us from doing calculations on excessive amounts of tiles, I plan on iterating over units rather than the entire world
    for u in units:
        if args.verbose:
            print("u is at", u.pos)
        affected_dict = influence_cities(
            u.pos, u.faction_id, radius, gmap, start_inf, decay, affected_dict
        )
    return affected_dict


def influenced_tiles_units(
    gmap: game_map.GameMap,
    units: list,
    radius: int,
    decay: int,
    start_inf: int,
    affected_dict: dict,
) -> dict:
    # to prevent us from doing calculations on excessive amounts of tiles, I plan on iterating over units rather than the entire world
    for u in units:
        if args.verbose:
            print("u is at", units[u].pos)
        affected_dict = influence_units(
            units[u].pos,
            units[u].faction_id,
            radius,
            gmap,
            start_inf,
            decay,
            affected_dict,
        )
    return affected_dict


# ###########################################################3
# GAME LOOP
# Where the magic happens.
# I've marked below where you might want to edit things
# for different reasons.
# ###########################################################


def GameLoop(display):

    winw, winh = pygame.display.get_window_size()

    # Width and Height (in cells) of the game map. If you want
    # a bigger/smaller map you will need to coordinate these values
    # with two other things.
    # - The window size below in main().
    # - The map_cell_size given in the Display class above.
    gmap = gen_game_map(MAP_WIDTH, MAP_HEIGHT)
    background = pygame.Surface((winw, winh))
    background.fill("brown")
    display.draw_map(gmap, background)

    factions = gen_factions(gmap)
    cities = gen_cities(gmap, list(factions.keys()))
    unit_dict = UnitDict(list(factions.keys()))

    # Starting game speed (real time between turns) in milliseconds.
    speed = 1024
    ticks = 0
    turn = 1
    pause = False
    padding = 6
    affected_dict = {}

    if DEBUG_MODE:
        came_from, cost_so_far = a_star(vec2.Vec2(5, 5), vec2.Vec2(28, 16), gmap)
        # for i in came_from:
        #     print(i, came_from[i])
        for i in reconstruct_path(came_from, vec2.Vec2(5, 5), vec2.Vec2(28, 16)):
            print(i[0], i[1])
    else:
        while display.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    display.run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        display.run = False
                    elif event.key == pygame.K_LEFT:

                        # Lower if you want a faster game speed.
                        if speed > 128:
                            speed = speed // 2
                    elif event.key == pygame.K_RIGHT:

                        # Increase if you want a slower game speed.
                        if speed < 4096:
                            speed = speed * 2
                    elif event.key == pygame.K_p:
                        # Pause the game.
                        pause = not pause
                        speed = 0 if pause else 1024

            if not pause:
                ticks += display.clock.tick(60)
                if ticks >= speed:
                    ticks = 0
                    cities_by_faction = {}
                    for fid, f in factions.items():
                        faction_cities = FactionPreTurn(cities, f)
                        cities_by_faction[fid] = faction_cities

                    commands = Turn(
                        factions, gmap, cities_by_faction, unit_dict.by_faction
                    )
                    RunAllCommands(commands, factions, unit_dict, cities, gmap)
                    turn += 1

                    game_over = CheckForGameOver(cities)
                    if game_over[0]:
                        print(f"Winning faction: {game_over[1]}")
                        display.run = False

                # display.draw_map(gmap, background)

                # ###########################################3
                # RIGHT_SIDE UI

                text_layer = pygame.Surface((winw, winh), pygame.SRCALPHA)

                text_turn, _ = display.font.render(f"TURN {turn}", "black")
                text_faction, _ = display.font.render(
                    f"{'Fctn':<5} {'Ci':>2} {'Un':>3} {'Mo':>4}", "black"
                )
                y = 30
                text_city = []
                greatest_width = 0
                greatest_height = 0
                for fid, f in factions.items():
                    num_cities = 0
                    for c in cities:
                        if c.faction_id == fid:
                            num_cities += 1

                    text_to_append = display.font.render(
                        f"{fid:<5} {num_cities:>2} {len(unit_dict.by_faction[fid]):>3} {f.money:>4}",
                        "black",
                    )[0]
                    if text_to_append.get_width() > greatest_width:
                        greatest_width = text_to_append.get_width()
                    if text_to_append.get_height() > greatest_height:
                        greatest_height = text_to_append.get_height()

                    text_city.append(
                        [
                            text_to_append,
                            y,
                        ]
                    )
                    y += 20
                origin_x = display.map_cell_size * (MAP_WIDTH + 0.5) * SCALE
                if args.verbose:
                    print(f"greatest_width: {greatest_width}")
                    print(f"greatest_height: {greatest_height}")
                draw_rectangle(
                    text_layer,
                    (
                        origin_x - padding,
                        0,
                        1920
                        - display.map_cell_size * (MAP_WIDTH + 0.5) * SCALE
                        + padding,
                        (y - greatest_height + padding) * SCALE,
                    ),
                    "white",
                    5,
                )

                for text in text_city:
                    text_layer.blit(
                        text[0],
                        (
                            origin_x,
                            text[1] * SCALE,
                        ),
                    )

                text_layer.blit(
                    text_turn,
                    dest=(origin_x, 5 * SCALE),
                )
                text_layer.blit(
                    text_faction,
                    (origin_x, 15 * SCALE),
                )
                for i in affected_dict:
                    gmap.cells[vec2.Vec2(i.x, i.y)].influences = [
                        [0, 0],
                        [0, 0],
                        [0, 0],
                    ]
                affected_dict.clear()
                affected_dict = influenced_tiles_cities(
                    gmap,
                    cities,
                    radius=2,
                    decay=1,
                    start_inf=5,
                    affected_dict=affected_dict,
                )
                affected_dict = influenced_tiles_units(
                    gmap,
                    unit_dict.by_pos,
                    radius=2,
                    decay=1,
                    start_inf=5,
                    affected_dict=affected_dict,
                )
                display.screen.blit(background, (0, 0))
                display.screen.blit(text_layer, (0, 0))
                display.draw_cities(cities, factions)
                display.draw_units(unit_dict, factions)
                if args.verbose:
                    display.draw_influence(gmap)
                pygame.display.flip()
            for g in gmap.cells:
                print("cell", g, gmap.cells[g].terrain.name, gmap.cells[g].influences)


def main():

    random.seed(None)
    display = init_display()
    GameLoop(display)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Jacob_Lorenzo_COS_598_Strategy_Game",
        description="Simulates a battle between two factions.",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    main()
