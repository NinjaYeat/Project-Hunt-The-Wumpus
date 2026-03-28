#! /usr/bin/env python3

import random
from collections import deque

ROWS     = 6
COLS     = 8
MUR      = 0
CAVERNE  = 1
COULOIR  = 2
NB_PUITS = 2

PARAMS = {
    "easy":   {"nb_cavernes": 16, "nb_corridors": 8,  "nb_chauves": 1},
    "medium": {"nb_cavernes": 12, "nb_corridors": 14, "nb_chauves": 2},
    "hard":   {"nb_cavernes": 8,  "nb_corridors": 20, "nb_chauves": 2},
}

DIRS    = [(-1, 0, "n"), (0, 1, "e"), (1, 0, "s"), (0, -1, "w")]
DIR_MAP = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
OPP     = {"n": "s", "s": "n", "e": "w", "w": "e"}

TILE_DIRS = {
    1: frozenset(["n", "e"]),
    2: frozenset(["n", "w"]),
    3: frozenset(["s", "e"]),
    4: frozenset(["s", "w"]),
    5: frozenset(["n", "s"]),
    6: frozenset(["e", "w"]),
}

TILE_NAME = {
    0: "roombase",
    1: "hallne",
    2: "hallnw",
    3: "hallse",
    4: "hallsw",
    5: "hallns",
    6: "hallew",
}


def _wrap(r, c):
    return r % ROWS, c % COLS


def _dir_vec(l):
    return next((dr, dc) for dr, dc, ll in DIRS if ll == l)


def _move_destination(tiles, py, px, dl):
    dr, dc   = _dir_vec(dl)
    nr, nc   = _wrap(py + dr, px + dc)
    from_dir = OPP[dl]

    if tiles[nr][nc] == 0:
        return nr, nc

    t = tiles[nr][nc]
    if from_dir in TILE_DIRS[t]:
        exit_l = next((l for l in TILE_DIRS[t] if l != from_dir), None)
        if exit_l:
            ddr, ddc = _dir_vec(exit_l)
            dest = _wrap(nr + ddr, nc + ddc)
            if tiles[dest[0]][dest[1]] == 0:
                return dest

    r2, c2 = _wrap(nr + dr, nc + dc)
    seen = {(nr, nc)}
    while tiles[r2][c2] != 0 and (r2, c2) not in seen:
        seen.add((r2, c2))
        r2, c2 = _wrap(r2 + dr, c2 + dc)
    return r2, c2


def _bfs_cavernes(tiles, start):
    vis = {start}
    q   = deque([start])
    while q:
        r, c = q.popleft()
        for _, _, l in DIRS:
            dest = _move_destination(tiles, r, c, l)
            if dest not in vis:
                vis.add(dest)
                q.append(dest)
    return vis


def _tout_connecte(tiles):
    cavernes = [(r, c) for r in range(ROWS) for c in range(COLS) if tiles[r][c] == 0]
    if not cavernes:
        return False
    return len(_bfs_cavernes(tiles, cavernes[0])) == len(cavernes)


def _generer(nb_corridors):
    tiles = [[0] * COLS for _ in range(ROWS)]
    types = list(TILE_DIRS.keys())

    placed = 0
    tries  = 0
    while placed < nb_corridors and tries < 10000:
        tries += 1
        r = random.randint(0, ROWS - 1)
        c = random.randint(0, COLS - 1)
        if tiles[r][c] != 0:
            continue

        random.shuffle(types)
        for t in types:
            backup = [row[:] for row in tiles]
            tiles[r][c] = t
            ok = True
            nouveaux = 1

            for dr, dc, l in DIRS:
                if l not in TILE_DIRS[t]:
                    continue
                nr, nc = _wrap(r + dr, c + dc)
                if tiles[nr][nc] != 0:
                    opp = OPP[l]
                    if opp not in TILE_DIRS[tiles[nr][nc]]:
                        ok = False
                        break
                    continue
                opp = OPP[l]
                compatibles = [tt for tt in types if opp in TILE_DIRS[tt]]
                random.shuffle(compatibles)
                placed_voisin = False
                for tt in compatibles:
                    tiles[nr][nc] = tt
                    if _tout_connecte(tiles):
                        placed_voisin = True
                        nouveaux += 1
                        break
                    tiles[nr][nc] = 0
                if not placed_voisin:
                    ok = False
                    break

            if ok and _tout_connecte(tiles):
                placed += nouveaux
                break
            for i in range(ROWS):
                tiles[i] = backup[i]

    return tiles


def _is_passable(tiles, r, c, direction):
    t = tiles[r][c]
    if t == 0:
        return True
    return direction.lower() in TILE_DIRS[t]


def _dist_cav(tiles, r1, c1, r2, c2):
    if (r1, c1) == (r2, c2):
        return 0
    vis = {(r1, c1): 0}
    q   = deque([(r1, c1, 0)])
    while q:
        r, c, d = q.popleft()
        for _, _, l in DIRS:
            dest = _move_destination(tiles, r, c, l)
            if dest not in vis:
                vis[dest] = d + 1
                if dest == (r2, c2):
                    return d + 1
                q.append((dest[0], dest[1], d + 1))
    return float("inf")


def _placer_entites(tiles, nb_puits, nb_chauves):
    cavernes = [(r, c) for r in range(ROWS) for c in range(COLS) if tiles[r][c] == 0]
    random.shuffle(cavernes)
    idx = 0

    ent = {
        "wumpus": None, "puits": [], "chauves": [],
        "joueur": None, "mousse": set(), "rouge": set()
    }

    ent["wumpus"]  = cavernes[idx]; idx += 1
    ent["puits"]   = [cavernes[idx + i] for i in range(nb_puits)]; idx += nb_puits
    ent["chauves"] = [cavernes[idx + i] for i in range(nb_chauves)]; idx += nb_chauves

    for pr, pc in ent["puits"]:
        for _, _, l in DIRS:
            dest = _move_destination(tiles, pr, pc, l)
            if list(dest) not in ent["puits"]:
                ent["mousse"].add(dest)             #j'ai retiré une ligne de code qui n'était pas forcèment utile c'est pour géré la mousse autour du puit correctement

    wr, wc = ent["wumpus"]
    for r in range(ROWS):
        for c in range(COLS):
            if tiles[r][c] == 0 and (r, c) != (wr, wc):
                if _dist_cav(tiles, wr, wc, r, c) <= 2:
                    ent["rouge"].add((r, c))

    interdits = set(ent["puits"]) | {ent["wumpus"]} | ent["mousse"]
    for pos in cavernes[idx:]:
        if pos not in interdits:
            ent["joueur"] = pos
            break

    return ent


def _bg_img(tiles, r, c, puits_s, mousse_s, rouge_s):
    t = tiles[r][c]
    if t != 0:
        return TILE_NAME[t]
    pos = (r, c)
    if pos in puits_s:
        return "roomnasty" if pos in rouge_s else "roompit"
    if pos in mousse_s and pos in rouge_s:
        return "roomnasty"
    if pos in mousse_s:
        return "roomslime"
    if pos in rouge_s:
        return "roomblood"
    return "roombase"


def _build_grid(tiles, wumpus_t, puits_s, chauves_s, mousse_s, rouge_s):
    grid = []
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            pos = (r, c)
            t   = tiles[r][c]
            if pos in puits_s:     ct = "slime"
            elif pos == wumpus_t:  ct = "wumpus"
            elif pos in chauves_s: ct = "bat"
            elif t != 0:           ct = "corridor"
            else:                  ct = "empty"
            row.append({
                "type":   ct,
                "bg_img": _bg_img(tiles, r, c, puits_s, mousse_s, rouge_s),
                "open_N": _is_passable(tiles, r, c, "N"),
                "open_S": _is_passable(tiles, r, c, "S"),
                "open_E": _is_passable(tiles, r, c, "E"),
                "open_W": _is_passable(tiles, r, c, "W"),
            })
        grid.append(row)
    return grid


def get_grid(state):
    tiles     = state["tiles"]
    wumpus_t  = tuple(state["wumpus"])
    puits_s   = set(map(tuple, state["puits"]))
    chauves_s = set(map(tuple, state["chauves_souris"]))
    mousse_s  = set(map(tuple, state["mousse"]))
    rouge_s   = set(map(tuple, state["rouge"]))
    return _build_grid(tiles, wumpus_t, puits_s, chauves_s, mousse_s, rouge_s)


def _calc_percepts(state):
    pos = (state["player"]["y"], state["player"]["x"])
    p   = []
    if pos in set(map(tuple, state["rouge"])):
        p.append("stench")
    if pos in set(map(tuple, state["mousse"])):
        p.append("breeze")
    return p


def new_game_state(difficulty="easy", mode="normal", vision="normal"):
    p      = PARAMS.get(difficulty, PARAMS["easy"])
    tiles  = _generer(p["nb_corridors"])
    ent    = _placer_entites(tiles, NB_PUITS, p["nb_chauves"])
    jr, jc = ent["joueur"]

    carte = [[CAVERNE if tiles[r][c] == 0 else COULOIR for c in range(COLS)]
             for r in range(ROWS)]

    state = {
        "h": ROWS,
        "w": COLS,
        "difficulty": difficulty,
        "mode": mode,
        "vision": vision,
        "tiles":          tiles,
        "carte":          carte,
        "wumpus":         list(ent["wumpus"]),
        "puits":          [list(p) for p in ent["puits"]],
        "chauves_souris": [list(b) for b in ent["chauves"]],
        "mousse":         [list(m) for m in ent["mousse"]],
        "rouge":          [list(r) for r in ent["rouge"]],
        "player":         {"y": jr, "x": jc},
        "last_dir":       "S",
        "revele":         [[True] * COLS for _ in range(ROWS)],
        "game_over":      False,
        "result":         None,
        "percepts":       [],
        "has_arrow":      True,
    }
    state["percepts"] = _calc_percepts(state)
    return state


def cell_is_visible(state, x, y):
    if state["vision"] == "blind":
        return state["player"]["x"] == x and state["player"]["y"] == y
    return state["revele"][y][x]


def move_player(state, direction):
    if state["game_over"]:
        return state

    dl = direction.lower()
    if dl not in OPP:
        return state

    tiles  = state["tiles"]
    py, px = state["player"]["y"], state["player"]["x"]
    tc     = tiles[py][px]

    if tc != 0 and dl not in TILE_DIRS[tc]:
        return state

    ny, nx = _move_destination(tiles, py, px, dl)

    dr, dc = _dir_vec(dl)
    r2, c2 = _wrap(py + dr, px + dc)
    seen   = set()
    while tiles[r2][c2] != 0 and (r2, c2) not in seen and (r2, c2) != (ny, nx):
        seen.add((r2, c2))
        state["revele"][r2][c2] = True
        r2, c2 = _wrap(r2 + dr, c2 + dc)

    state["player"]["y"]    = ny
    state["player"]["x"]    = nx
    state["last_dir"]       = direction
    state["revele"][ny][nx] = True

    if [ny, nx] in state["puits"]:
        state["game_over"] = True
        state["result"]    = "dead_slime"
        _reveler_tout(state)
        return state

    if [ny, nx] == state["wumpus"]:
        state["game_over"] = True
        state["result"]    = "dead_wumpus"
        _reveler_tout(state)
        return state

    state = _check_bat(state, ny, nx)
    if not state["game_over"]:
        state["percepts"] = _calc_percepts(state)
    return state


def _check_bat(state, r, c):
    if [r, c] not in state["chauves_souris"]:
        return state

    tiles     = state["tiles"]
    interdits = [state["wumpus"]] + state["puits"]
    libre     = [
        [row, col] for row in range(ROWS) for col in range(COLS)
        if tiles[row][col] == 0
        and [row, col] not in interdits
        and [row, col] != [r, c]
    ]                                            #ici aussi j'ai retiré la condition if i < 2 car ça va directement laisser une chance au gars appart si il faut en laissé une puis qu'il se fasse tp  a toi de voir nono du binks !

    if not libre:
        return state

    dest = random.choice(libre)
    state["player"]["y"]              = dest[0]
    state["player"]["x"]              = dest[1]
    state["revele"][dest[0]][dest[1]] = True

    autres = [p for p in libre if p != dest]
    if autres:
        i = state["chauves_souris"].index([r, c])
        state["chauves_souris"][i] = random.choice(autres)

    if dest in state["puits"]:
        state["game_over"] = True
        state["result"]    = "dead_slime"
        _reveler_tout(state)
    elif dest == state["wumpus"]:
        state["game_over"] = True
        state["result"]    = "dead_wumpus"
        _reveler_tout(state)

    return state


def shoot_arrow(state, direction):
    if state["game_over"] or not state["has_arrow"]:
        return state

    state["has_arrow"] = False
    dl     = direction.lower()
    tiles  = state["tiles"]
    py, px = state["player"]["y"], state["player"]["x"]
    visited = {(py, px)}

    r, c = _move_destination(tiles, py, px, dl)
    while (r, c) not in visited:
        if [r, c] == state["wumpus"]:
            state["game_over"] = True
            state["result"]    = "win"
            _reveler_tout(state)
            return state
        visited.add((r, c))
        r, c = _move_destination(tiles, r, c, dl)

    state["game_over"] = True
    state["result"]    = "missed_wumpus"
    _reveler_tout(state)
    return state


def _reveler_tout(state):
    state["revele"] = [[True] * COLS for _ in range(ROWS)]