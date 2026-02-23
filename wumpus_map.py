#! /usr/bin/env python3
import random

W = 8
H = 6

WUMPUS = "wumpus"
SLIME = "slime"
BAT = "bat"
EMPTY = "empty"


def new_game_state(difficulty="easy", mode="normal", vision="normal"):
    grid = [[{"seen": False, "type": EMPTY} for _ in range(W)] for _ in range(H)]

    px, py = 0, 0
    grid[py][px]["seen"] = True

    state = {
        "w": W,
        "h": H,
        "grid": grid,
        "player": {"x": px, "y": py},
        "difficulty": difficulty,
        "mode": mode,
        "vision": vision,
        "game_over": False,
        "result": None,
        "percepts": [],
        "has_arrow": True,
        "bat_visits": {},
    }


    # 2 puits fixes
    for _ in range(2):
        x, y = _random_empty_cell(state)
        state["grid"][y][x]["type"] = SLIME

    # Wumpus
    wx, wy = _random_empty_cell(state)
    state["grid"][wy][wx]["type"] = WUMPUS

    # Chauves-souris
    nb_bats = 1 if difficulty == "easy" else 2
    for _ in range(nb_bats):
        bx, by = _random_empty_cell(state)
        state["grid"][by][bx]["type"] = BAT
        state["bat_visits"][f"{bx},{by}"] = 0

    state["percepts"] = compute_percepts(state)
    return state


def _random_empty_cell(state):
    while True:
        x = random.randrange(state["w"])
        y = random.randrange(state["h"])
        if (x, y) == (0, 0):
            continue
        if state["grid"][y][x]["type"] == EMPTY:
            return x, y


def _in_bounds(state, x, y):
    return 0 <= x < state["w"] and 0 <= y < state["h"]


def _neighbors4(state, x, y):
    for dx, dy in ((0,-1),(0,1),(-1,0),(1,0)):
        nx, ny = x+dx, y+dy
        if _in_bounds(state, nx, ny):
            yield nx, ny


# PERCEPTS

def compute_percepts(state):
    px = state["player"]["x"]
    py = state["player"]["y"]

    percepts = []

    for y in range(state["h"]):
        for x in range(state["w"]):
            if state["grid"][y][x]["type"] == WUMPUS:
                if abs(px - x) + abs(py - y) <= 2 and (px, py) != (x, y):
                    percepts.append("stench")

    for nx, ny in _neighbors4(state, px, py):
        if state["grid"][ny][nx]["type"] == SLIME:
            percepts.append("breeze")

    return percepts


# DEPLACEMENT
def _step_from_dir(dir_):
    if dir_ == "N": return (0, -1)
    if dir_ == "S": return (0, 1)
    if dir_ == "W": return (-1, 0)
    if dir_ == "E": return (1, 0)
    return (0, 0)


def move_player(state, dir_):
    if state["game_over"]:
        return state

    if dir_ not in ("N", "S", "E", "W"):
        return state

    dx, dy = _step_from_dir(dir_)

    def do_step():
        nx = state["player"]["x"] + dx
        ny = state["player"]["y"] + dy

        if not _in_bounds(state, nx, ny):
            return False

        state["player"]["x"] = nx
        state["player"]["y"] = ny
        state["grid"][ny][nx]["seen"] = True

        cell_type = state["grid"][ny][nx]["type"]

        # Mort directe
        if cell_type == WUMPUS:
            state["game_over"] = True
            state["result"] = "dead_wumpus"

        elif cell_type == SLIME:
            state["game_over"] = True
            state["result"] = "dead_slime"

        elif cell_type == BAT:
            _handle_bat(state, nx, ny)

        state["percepts"] = compute_percepts(state)
        return True

    # Mode express
    if state["mode"] == "express":
        while True:
            ok = do_step()
            if not ok or state["game_over"]:
                break
        return state

    do_step()
    return state


# CHAUVE-SOURIS

def _handle_bat(state, x, y):
    key = (x, y)
    state["bat_visits"][key] += 1

    if state["bat_visits"][key] >= 2:
        while True:
            rx = random.randrange(state["w"])
            ry = random.randrange(state["h"])
            t = state["grid"][ry][rx]["type"]
            if t not in (WUMPUS, SLIME):
                break

        state["player"]["x"] = rx
        state["player"]["y"] = ry
        state["grid"][ry][rx]["seen"] = True

        # La chauve-souris déménag
        nx, ny = _random_empty_cell(state)
        state["grid"][ny][nx]["type"] = BAT
        state["bat_visits"][(nx, ny)] = 0
        state["grid"][y][x]["type"] = EMPTY


# AFFICHAGE

def cell_is_visible(state, x, y):
    if state["game_over"]:
        return True
    if state["vision"] == "blind":
        return (x == state["player"]["x"] and y == state["player"]["y"])
    return state["grid"][y][x]["seen"]