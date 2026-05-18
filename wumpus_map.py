#! /usr/bin/env python3

import random
from collections import deque

ROWS = 6 # Ligne
COLS = 8 # Colonne
CAVERN = 1 # Caverne
CORRIDOR = 2 # Corridor
NB_WELL = 2 # Nombre de puits

# Nombres des cavernes, corridors et chauves-souris selon les niveaux
PARAMS = {
    "easy": {"nb_caverns": 16, "nb_corridors": 8,  "nb_bat": 1},
    "medium": {"nb_caverns": 12, "nb_corridors": 14, "nb_bat": 2},
    "hard": {"nb_caverns": 8,  "nb_corridors": 20, "nb_bat": 2},
}

# Tuples qui gèrent les directions cardinales
DIRS = [(-1, 0, "n"), (0, 1, "e"), (1, 0, "s"), (0, -1, "w")]
OPP = {"n": "s", "s": "n", "e": "w", "w": "e"}

# Ces types permettent de relier deux corridors incompatibles dans la même case
TILE_DIRS = {
    1: frozenset(["n", "e"]), # hallne
    2: frozenset(["n", "w"]), # hallnw
    3: frozenset(["s", "e"]), # hallse
    4: frozenset(["s", "w"]), # hallsw
    5: frozenset(["n", "e", "s", "w"]), # hallne + hallsw
    6: frozenset(["n", "e", "s", "w"]), # hallnw + hallse
}

# Entrée => sortie exacte pour chaque type de corridor
EXIT_MAP = {
    1: {"n": "e", "e": "n"},
    2: {"n": "w", "w": "n"},
    3: {"s": "e", "e": "s"},
    4: {"s": "w", "w": "s"},
    5: {"n": "e", "e": "n", "s": "w", "w": "s"},
    6: {"n": "w", "w": "n", "s": "e", "e": "s"},
}

# Associe un identifiant de tuile à un nom de sprite
TILE_NAME = {
    0: "roombase",
    1: "hallne",
    2: "hallnw",
    3: "hallse",
    4: "hallsw",
    5: "hallnesw",
    6: "hallnwse",
}

# Quand un corridor bloque le passage, on l'améliore vers un type combiné
UPGRADE_MAP = {1: 5, 4: 5, 2: 6, 3: 6, 5: 5, 6: 6}


# Fonction wrap : si on dépasse les bords de la map, on revient de l'autre côté
def _wrap(r, c):
    return r % ROWS, c % COLS


# Convertit une lettre de direction en déplacement ligne/colonne
def _dir_vec(l):
    return next((dr, dc) for dr, dc, ll in DIRS if ll == l)


# Fonction qui détermine où le personnage arrive à la fin du déplacement
def _move_destination(tiles, py, px, dl):
    path = _move_path(tiles, py, px, dl)
    if not path:
        return py, px
    return path[-1]


# Fonction qui récupère tout le chemin parcouru, y compris les couloirs
# Elle sert à révéler les corridors traversés sur la map
def _move_path(tiles, py, px, dl):
    path = []

    dr, dc = _dir_vec(dl)
    r, c = _wrap(py + dr, px + dc)

    # Si la case juste à côté est une caverne, le chemin contient seulement cette case
    if tiles[r][c] == 0:
        return [(r, c)]

    # Direction par laquelle on entre dans le corridor
    entry_dir = OPP[dl]
    seen = set()

    while tiles[r][c] != 0:
        # Évite les boucles infinies dans les corridors
        if (r, c, entry_dir) in seen:
            return []

        seen.add((r, c, entry_dir))
        path.append((r, c))

        t = tiles[r][c]

        # Si on entre par un côté fermé, le déplacement est impossible
        if entry_dir not in EXIT_MAP[t]:
            return []

        # On ressort par la vraie sortie du corridor
        exit_dir = EXIT_MAP[t][entry_dir]
        dr, dc = _dir_vec(exit_dir)

        r, c = _wrap(r + dr, c + dc)

        # Pour le prochain corridor, on entre depuis le côté opposé
        entry_dir = OPP[exit_dir]

    # Ajoute la caverne d'arrivée
    path.append((r, c))
    return path


# Fonction qui explore toutes les cavernes accessibles depuis une position de départ
def _bfs_caverns(tiles, start):
    vis = {start}
    q = deque([start])

    while q:
        r, c = q.popleft()
        for _, _, l in DIRS:
            dest = _move_destination(tiles, r, c, l)
            if dest not in vis:
                vis.add(dest)
                q.append(dest)

    return vis


# Fonction qui vérifie si toutes les cavernes sont connectées entre elles
def _all_connected(tiles):
    cavernes = [(r, c) for r in range(ROWS) for c in range(COLS) if tiles[r][c] == 0]
    if not cavernes:
        return False
    return len(_bfs_caverns(tiles, cavernes[0])) == len(cavernes)


# Fonction qui génère une grille complète de corridors
def _generate_full_grid():
    tiles = [[0] * COLS for _ in range(ROWS)]

    for r in range(ROWS):
        for c in range(COLS):
            # Contraintes Nord
            if r > 0:
                north_neighbor = tiles[r - 1][c]
                must_have_north = "s" in TILE_DIRS.get(north_neighbor, set())
                forbid_north = "s" not in TILE_DIRS.get(north_neighbor, set())
            else:
                must_have_north = False
                forbid_north = True

            # Contraintes Ouest
            if c > 0:
                west_neighbor = tiles[r][c - 1]
                must_have_west = "e" in TILE_DIRS.get(west_neighbor, set())
                forbid_west = "e" not in TILE_DIRS.get(west_neighbor, set())
            else:
                must_have_west = False
                forbid_west = True

            forbid_east = c == COLS - 1
            forbid_south = r == ROWS - 1

            compatibles = []
            for t in [1, 2, 3, 4]:
                dirs = TILE_DIRS[t]
                if must_have_north and "n" not in dirs: continue
                if must_have_west and "w" not in dirs: continue
                if forbid_north and "n" in dirs: continue
                if forbid_west and "w" in dirs: continue
                if forbid_east and "e" in dirs: continue
                if forbid_south and "s" in dirs: continue
                compatibles.append(t)

            if not compatibles:
                return None

            tiles[r][c] = random.choice(compatibles)

    return tiles


# Corrige les blocages en transformant certains corridors en corridors combinés
def _fix_dead_ends(tiles):
    changed = True

    while changed:
        changed = False

        for r in range(ROWS):
            for c in range(COLS):
                for dr, dc, dl in DIRS:
                    nr, nc = _wrap(r + dr, c + dc)
                    t_voisin = tiles[nr][nc]

                    if t_voisin == 0:
                        continue

                    entry_at_voisin = OPP[dl]

                    if entry_at_voisin not in EXIT_MAP[t_voisin]:
                        new_type = UPGRADE_MAP[t_voisin]

                        if new_type != t_voisin:
                            tiles[nr][nc] = new_type
                            changed = True


# Fonction qui génère une grille jouable avec le bon nombre de corridors
def _generate(nb_corridors):
    nb_cavernes = ROWS * COLS - nb_corridors

    for _ in range(1000):
        tiles = _generate_full_grid()

        if tiles is None:
            continue

        toutes = [(r, c) for r in range(ROWS) for c in range(COLS)]
        random.shuffle(toutes)
        cavernes_choisies = toutes[:nb_cavernes]

        for r, c in cavernes_choisies:
            tiles[r][c] = 0

        # Corrige les dead-ends avant de vérifier la connectivité
        _fix_dead_ends(tiles)

        if _all_connected(tiles):
            return tiles

    return tiles


# Vérifie si une direction est accessible depuis une case donnée
def _is_passable(tiles, r, c, direction):
    t = tiles[r][c]
    if t == 0:
        return True
    return direction.lower() in TILE_DIRS[t]


# Calcule la distance entre deux cavernes
def _dist_cav(tiles, r1, c1, r2, c2):
    if (r1, c1) == (r2, c2):
        return 0

    vis = {(r1, c1): 0}
    q = deque([(r1, c1, 0)])

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


# Place le joueur, le wumpus, les puits et les chauves-souris
def _place_entities(tiles, nb_well, nb_bat):
    cavernes = [(r, c) for r in range(ROWS) for c in range(COLS) if tiles[r][c] == 0]
    random.shuffle(cavernes)
    idx = 0

    ent = {
        "wumpus": None,
        "well": [],
        "bat": [],
        "player": None,
        "foam": set(),
        "red": set(),
    }

    ent["wumpus"] = cavernes[idx]
    idx += 1

    ent["well"] = [cavernes[idx + i] for i in range(nb_well)]
    idx += nb_well

    ent["bat"] = [cavernes[idx + i] for i in range(nb_bat)]
    idx += nb_bat

    # Mousse dans les cavernes adjacentes aux puits
    for pr, pc in ent["well"]:
        for _, _, l in DIRS:
            dest = _move_destination(tiles, pr, pc, l)
            if dest not in ent["well"]:
                ent["foam"].add(dest)

    # Rouge dans les cavernes à distance <= 2 du wumpus
    wr, wc = ent["wumpus"]
    for r in range(ROWS):
        for c in range(COLS):
            if tiles[r][c] == 0 and (r, c) != (wr, wc):
                if _dist_cav(tiles, wr, wc, r, c) <= 2:
                    ent["red"].add((r, c))

    # Joueur placé dans une caverne sûre
    interdits = set(ent["well"]) | {ent["wumpus"]} | ent["foam"]

    for pos in cavernes[idx:]:
        if pos not in interdits:
            ent["player"] = pos
            break

    return ent


# Détermine le sprite de fond à afficher selon la case
def _bg_img(tiles, r, c, well_s, foam_s, red_s):
    t = tiles[r][c]

    if t != 0:
        return TILE_NAME[t]

    pos = (r, c)

    if pos in well_s:
        return "roomnasty" if pos in red_s else "roompit"
    if pos in foam_s and pos in red_s:
        return "roomnasty"
    if pos in foam_s:
        return "roomslime"
    if pos in red_s:
        return "roomblood"

    return "roombase"


# Construit la grille envoyée au HTML
def _build_grid(tiles, wumpus_t, well_s, bat_s, foam_s, red_s):
    grid = []

    for r in range(ROWS):
        row = []

        for c in range(COLS):
            pos = (r, c)
            t = tiles[r][c]

            if pos in well_s:
                ct = "slime"
            elif pos == wumpus_t:
                ct = "wumpus"
            elif pos in bat_s:
                ct = "bat"
            elif t != 0:
                ct = "corridor"
            else:
                ct = "empty"

            row.append({
                "type": ct,
                "bg_img": _bg_img(tiles, r, c, well_s, foam_s, red_s),
                "open_N": _is_passable(tiles, r, c, "N"),
                "open_S": _is_passable(tiles, r, c, "S"),
                "open_E": _is_passable(tiles, r, c, "E"),
                "open_W": _is_passable(tiles, r, c, "W"),
            })

        grid.append(row)

    return grid


# Transforme l'état du jeu en grille affichable
def get_grid(state):
    tiles = state["tiles"]
    wumpus_t = tuple(state["wumpus"])
    puits_s = set(map(tuple, state["well"]))
    chauves_s = set(map(tuple, state["bat"]))
    mousse_s = set(map(tuple, state["foam"]))
    rouge_s = set(map(tuple, state["red"]))

    return _build_grid(tiles, wumpus_t, puits_s, chauves_s, mousse_s, rouge_s)


# Calcule les perceptions du joueur
def _calc_percepts(state):
    pos = (state["player"]["y"], state["player"]["x"])
    p = []

    if pos in set(map(tuple, state["red"])):
        p.append("stench")
    if pos in set(map(tuple, state["foam"])):
        p.append("breeze")

    return p


# Initialise une nouvelle partie
def new_game_state(difficulty="easy", mode="normal", vision="normal"):
    p = PARAMS.get(difficulty, PARAMS["easy"])
    tiles = _generate(p["nb_corridors"])
    ent = _place_entities(tiles, NB_WELL, p["nb_bat"])
    jr, jc = ent["player"]

    grid_map = [
        [CAVERN if tiles[r][c] == 0 else CORRIDOR for c in range(COLS)]
        for r in range(ROWS)
    ]

    state = {
        "h": ROWS,
        "w": COLS,
        "difficulty": difficulty,
        "mode": mode,
        "vision": vision,
        "tiles": tiles,
        "map": grid_map,
        "wumpus": list(ent["wumpus"]),
        "well": [list(p) for p in ent["well"]],
        "bat": [list(b) for b in ent["bat"]],
        "foam": [list(m) for m in ent["foam"]],
        "red": [list(r) for r in ent["red"]],
        "player": {"y": jr, "x": jc},
        "last_dir": "S",
        "reveals": [[False] * COLS for _ in range(ROWS)],
        "game_over": False,
        "result": None,
        "percepts": [],
        "has_arrow": True,
    }

    # Au début, seule la case du joueur est visible
    state["reveals"][jr][jc] = True
    state["percepts"] = _calc_percepts(state)

    return state


# Détermine si une case est visible selon le mode de vision
def cell_is_visible(state, x, y):
    if state["vision"] == "blind":
        return state["player"]["x"] == x and state["player"]["y"] == y
    return state["reveals"][y][x]


# Gère ce qui arrive quand le joueur arrive sur une case
def _handle_arrival(state, ny, nx):
    if [ny, nx] in state["well"]:
        state["game_over"] = True
        state["result"] = "dead_slime"
        _reveal_all(state)
        return state, True

    if [ny, nx] == state["wumpus"]:
        state["game_over"] = True
        state["result"] = "dead_wumpus"
        _reveal_all(state)
        return state, True

    hit_bat = [ny, nx] in state["bat"]
    state = _check_bat(state, ny, nx)

    if not state["game_over"]:
        state["percepts"] = _calc_percepts(state)

    return state, hit_bat


# Déplace le joueur en mode normal ou express
def move_player(state, direction):
    if state["game_over"]:
        return state

    dl = direction.lower()

    if dl not in OPP:
        return state

    tiles = state["tiles"]

    def do_one_move():
        py = state["player"]["y"]
        px = state["player"]["x"]
        tc = tiles[py][px]

        if tc != 0 and tc in TILE_DIRS and dl not in TILE_DIRS[tc]:
            return False

        path = _move_path(tiles, py, px, dl)

        if not path:
            return False

        ny, nx = path[-1]

        if (ny, nx) == (py, px):
            return False

        # Révèle toutes les cases traversées, y compris les couloirs
        for ry, rx in path:
            state["reveals"][ry][rx] = True

        state["player"]["y"] = ny
        state["player"]["x"] = nx
        state["last_dir"] = direction

        state_after, must_stop = _handle_arrival(state, ny, nx)

        return not must_stop and not state_after["game_over"]

    # Mode normal : un seul déplacement
    if state.get("mode") != "express":
        do_one_move()
        return state

    # Mode express :
    # avance jusqu'au bord
    # ne traverse pas automatiquement
    # si le joueur est déjà au bord et appuie encore, il traverse
    moved = False
    seen = {(state["player"]["y"], state["player"]["x"])}

    for _ in range(ROWS * COLS):
        py = state["player"]["y"]
        px = state["player"]["x"]
        dr, dc = _dir_vec(dl)

        next_r = py + dr
        next_c = px + dc

        is_leaving_map = (
            next_r < 0 or next_r >= ROWS or
            next_c < 0 or next_c >= COLS
        )

        if is_leaving_map and moved:
            break

        can_continue = do_one_move()
        moved = True

        pos = (state["player"]["y"], state["player"]["x"])

        if not can_continue:
            break

        if is_leaving_map:
            break

        if pos in seen:
            break

        seen.add(pos)

    return state


# Gère la téléportation du joueur avec une chauve-souris
def _check_bat(state, r, c):
    if [r, c] not in state["bat"]:
        return state

    tiles = state["tiles"]
    forbidden = [state["wumpus"]] + state["well"]

    free = [
        [row, col]
        for row in range(ROWS)
        for col in range(COLS)
        if tiles[row][col] == 0
        and [row, col] not in forbidden
        and [row, col] != [r, c]
    ]

    if not free:
        return state

    dest = random.choice(free)
    state["player"]["y"] = dest[0]
    state["player"]["x"] = dest[1]
    state["reveals"][dest[0]][dest[1]] = True

    other = [p for p in free if p != dest]

    if other:
        i = state["bat"].index([r, c])
        state["bat"][i] = random.choice(other)

    if dest in state["well"]:
        state["game_over"] = True
        state["result"] = "dead_slime"
        _reveal_all(state)
    elif dest == state["wumpus"]:
        state["game_over"] = True
        state["result"] = "dead_wumpus"
        _reveal_all(state)

    return state


# Gère le tir de la flèche
def shoot_arrow(state, direction):
    if state["game_over"] or not state["has_arrow"]:
        return state

    state["has_arrow"] = False

    dl = direction.lower()
    tiles = state["tiles"]
    py = state["player"]["y"]
    px = state["player"]["x"]
    visited = {(py, px)}

    r, c = _move_destination(tiles, py, px, dl)

    while (r, c) not in visited:
        if [r, c] == state["wumpus"]:
            state["game_over"] = True
            state["result"] = "win"
            _reveal_all(state)
            return state

        visited.add((r, c))
        r, c = _move_destination(tiles, r, c, dl)

    state["game_over"] = True
    state["result"] = "missed_wumpus"
    _reveal_all(state)

    return state


# Révèle toute la carte à la fin de la partie
def _reveal_all(state):
    state["reveals"] = [[True] * COLS for _ in range(ROWS)]