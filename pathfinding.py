import vec2
import heapq
from typing import Optional
import game_map
from params import *


def doublewidth_distance_vt(a: vec2.Vec2, b: tuple) -> int:
    dcol = abs(a.x - b[0])
    drow = abs(a.y - b[1])
    return drow + max(0, (dcol - drow) / 2)


def doublewidth_distance_tp(a: tuple, b: tuple) -> int:
    dcol = abs(a[0] - b[0])
    drow = abs(a[1] - b[1])
    return drow + max(0, (dcol - drow) / 2)


def doublewidth_distance(a: vec2.Vec2, b: vec2.Vec2) -> int:
    dcol = abs(a.x - b.x)
    drow = abs(a.y - b.y)
    return drow + max(0, (dcol - drow) / 2)


def heuristic(start, goal):
    return doublewidth_distance(start, goal)


def get_neighbors(gmap, coord):
    neighbors = []
    for direction, delta in vec2.MOVES.items():
        new_pos = coord + delta
        new_pos.mod(gmap.width, gmap.height)

        neighbors.append((new_pos, direction))
    return neighbors


def precomputed_neighbors(gmap):
    precomputed_neighbors = {}
    for cell in gmap.cells:
        precomputed_neighbors[cell] = get_neighbors(gmap, cell)
    return precomputed_neighbors


CELL_NEIGHBORS = precomputed_neighbors(game_map.GameMap(MAP_WIDTH, MAP_HEIGHT))


def reconstruct_path(
    came_from: dict[vec2.Vec2, str, vec2.Vec2], start: vec2.Vec2, goal: vec2.Vec2
):
    current = goal
    path = []
    if goal not in came_from:
        return []
    while current != start:
        prev, direction = came_from[current]
        path.append((current, direction))
        current = prev

    return path


path_hash_cache = {}


def a_star(
    start: vec2.Vec2,
    goal: vec2.Vec2,
    gmap: game_map.GameMap,
    unit_dict: dict,
    faction_id: str,
):
    cache_key = (start, goal)
    if path_hash_cache.get(cache_key) is not None:
        return path_hash_cache[cache_key]
    frontier = []
    heapq.heappush(frontier, (0, (start, None)))

    came_from: dict[vec2.Vec2, str, Optional[vec2.Vec2]] = {}
    cost_so_far: dict[vec2.Vec2, float] = {}

    came_from[start] = None
    cost_so_far[start] = 0

    while frontier:
        priority, current = heapq.heappop(frontier)

        if current[0] == goal:
            break

        for next_pos, direction in CELL_NEIGHBORS[current[0]]:

            if unit_dict is not None and next_pos in unit_dict.by_pos:
                other_unit = unit_dict.by_pos[next_pos]
                if other_unit.faction_id == faction_id and next_pos != goal:
                    continue

            new_cost = cost_so_far[current[0]] + gmap.get_cell(next_pos).cost

            if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                cost_so_far[next_pos] = new_cost
                priority = new_cost + heuristic(next_pos, goal)
                heapq.heappush(frontier, (priority, (next_pos, direction)))
                came_from[next_pos] = (current[0], direction)

    path_hash_cache[cache_key] = (came_from, cost_so_far)
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


def precomputed_offsets(radius):
    offsets = []
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            dist = doublewidth_distance_tp((0, 0), (dx, dy))
            if dist <= radius:
                offsets.append((dx, dy, dist))
    return offsets


OFFSETS_RADIUS_2 = precomputed_offsets(2)


def influence_cities(
    center_coords: vec2.Vec2,
    faction_id: str,
    gmap: game_map.GameMap,
    start_inf: int,
    decay: int,
    affected_dict: dict,
) -> dict:
    for dx, dy, dist in OFFSETS_RADIUS_2:
        tile_y = center_coords.y + dy

        if 0 <= tile_y < MAP_HEIGHT:
            tile_x = center_coords.x + dx * 2

            if tile_y % 2 == 1 and center_coords.y % 2 == 0:
                tile_x += 1
            if tile_y % 2 == 0 and center_coords.y % 2 == 1:
                tile_x -= 1
            if 0 <= tile_x < MAP_WIDTH * 2:
                if gmap.cells.get(vec2.Vec2(tile_x, tile_y)) is not None:
                    if faction_id == "Red":
                        gmap.cells[vec2.Vec2(tile_x, tile_y)].influences[0][0] += max(
                            0, start_inf - dist * decay
                        )

                        gmap = assign_influence(
                            gmap,
                            vec2.Vec2(tile_x, tile_y),
                            0,
                            0,
                            start_inf,
                            dist,
                            decay,
                        )
                        gmap.highest["Red"].append(
                            [
                                gmap.cells[vec2.Vec2(tile_x, tile_y)].influences[0][0],
                                vec2.Vec2(tile_x, tile_y),
                            ]
                        )
                        offense = gmap.cells[vec2.Vec2(tile_x, tile_y)].get_influence(
                            "Blue", 1
                        )
                        if offense > 0:
                            gmap.threats["Blue"].append(
                                [
                                    vec2.Vec2(tile_x, tile_y),
                                    offense
                                    + gmap.cells[
                                        vec2.Vec2(tile_x, tile_y)
                                    ].get_attack_mod(),
                                ]
                            )

                        if affected_dict.get(vec2.Vec2(tile_x, tile_y), None) is None:
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
                        gmap.highest["Blue"].append(
                            [
                                gmap.cells[vec2.Vec2(tile_x, tile_y)].influences[0][1],
                                vec2.Vec2(tile_x, tile_y),
                            ]
                        )
                        offense = gmap.cells[vec2.Vec2(tile_x, tile_y)].get_influence(
                            "Red", 1
                        )
                        if offense > 0:
                            gmap.threats["Red"].append(
                                [
                                    vec2.Vec2(tile_x, tile_y),
                                    offense
                                    + gmap.cells[
                                        vec2.Vec2(tile_x, tile_y)
                                    ].get_attack_mod(),
                                ]
                            )
                        if affected_dict.get(vec2.Vec2(tile_x, tile_y), None) is None:
                            affected_dict[vec2.Vec2(tile_x, tile_y)] = ""
                else:
                    print(f"Tile ({tile_x}, {tile_y}) is out of bounds for the map.")
    return affected_dict


def influence_units(
    center_coords: vec2.Vec2,
    faction_id: str,
    gmap: game_map.GameMap,
    start_inf: int,
    decay: int,
    affected_dict: dict,
) -> dict:
    for dx, dy, dist in OFFSETS_RADIUS_2:
        tile_y = center_coords.y + dy

        if 0 <= tile_y < MAP_HEIGHT:
            tile_x = center_coords.x + dx * 2

            if tile_y % 2 == 1 and center_coords.y % 2 == 0:
                tile_x += 1
            if tile_y % 2 == 0 and center_coords.y % 2 == 1:
                tile_x -= 1
            if 0 <= tile_x < MAP_WIDTH * 2:
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

                        if affected_dict.get(vec2.Vec2(tile_x, tile_y), None) is None:
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

                        if affected_dict.get(vec2.Vec2(tile_x, tile_y), None) is None:
                            affected_dict[vec2.Vec2(tile_x, tile_y)] = ""
                else:
                    print(f"Tile ({tile_x}, {tile_y}) is out of bounds for the map.")
    return affected_dict


def influenced_tiles_cities(
    gmap: game_map.GameMap,
    units: list,
    decay: int,
    start_inf: int,
    affected_dict: dict,
) -> dict:
    for u in units:
        affected_dict = influence_cities(
            u.pos, u.faction_id, gmap, start_inf, decay, affected_dict
        )
    return affected_dict


def influenced_tiles_units(
    gmap: game_map.GameMap,
    units: list,
    decay: int,
    start_inf: int,
    affected_dict: dict,
) -> dict:
    for u in units:
        affected_dict = influence_units(
            units[u].pos,
            units[u].faction_id,
            gmap,
            start_inf,
            decay,
            affected_dict,
        )
    return affected_dict
