#! /usr/bin/env python3
import random

W = 8
H = 6

def new_game_state(difficulty="easy", mode="normal", vision="normal"):
    grid = [[{"seen": False, "type": "empty"} for _ in range(W)] for _ in range(H)]

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
    }
    return state


def _in_bounds(state, x, y):
    return 0 <= x < state["w"] and 0 <= y < state["h"]


def _step_from_dir(dir_):
    if dir_ == "N":
        return (0, -1)
    if dir_ == "S":
        return (0, 1)
    if dir_ == "W":
        return (-1, 0)
    if dir_ == "E":
        return (1, 0)
    return (0, 0)


def can_move(state, dir_):
    dx, dy = _step_from_dir(dir_)
    x = state["player"]["x"] + dx
    y = state["player"]["y"] + dy
    return _in_bounds(state, x, y)


def move_player(state, dir_):
    if state.get("game_over"):
        return state

    if dir_ not in ("N", "E", "S", "W"):
        return state

    dx, dy = _step_from_dir(dir_)

    def do_one_step():
        nx = state["player"]["x"] + dx
        ny = state["player"]["y"] + dy
        if not _in_bounds(state, nx, ny):
            return False

        state["player"]["x"] = nx
        state["player"]["y"] = ny
        state["grid"][ny][nx]["seen"] = True
        return True

    if state.get("mode") == "express":
        moved = False
        while True:
            ok = do_one_step()
            if not ok:
                break
            moved = True
        return state

    do_one_step()
    return state


def cell_is_visible(state, x, y):
    if state.get("vision") == "blind":
        return (x == state["player"]["x"] and y == state["player"]["y"])
    return bool(state["grid"][y][x]["seen"])