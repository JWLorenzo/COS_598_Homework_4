import vec2
from queue import PriorityQueue
from typing import Optional
import game_map
from params import *


def doublewidth_distance_vt(a: vec2.Vec2, b: tuple) -> int:
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
                    dist = doublewidth_distance_vt(center_coords, (tile_x, tile_y))
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
                                    len(gmap.objectives["Red"]) == 0
                                    or gmap.cells[vec2.Vec2(tile_x, tile_y)].influences[
                                        0
                                    ][0]
                                    > gmap.objectives["Red"][0]
                                ):
                                    gmap.objectives["Red"] = [
                                        gmap.cells[
                                            vec2.Vec2(tile_x, tile_y)
                                        ].influences[0][0],
                                        vec2.Vec2(tile_x, tile_y),
                                    ]

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
                                    len(gmap.objectives["Blue"]) == 0
                                    or gmap.cells[vec2.Vec2(tile_x, tile_y)].influences[
                                        0
                                    ][1]
                                    > gmap.objectives["Blue"][0]
                                ):
                                    gmap.objectives["Blue"] = [
                                        gmap.cells[
                                            vec2.Vec2(tile_x, tile_y)
                                        ].influences[0][1],
                                        vec2.Vec2(tile_x, tile_y),
                                    ]

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
                    dist = doublewidth_distance_vt(center_coords, (tile_x, tile_y))
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
