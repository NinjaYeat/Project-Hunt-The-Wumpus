#! /usr/bin/env python3

import random
from collections import deque

ROWS = 6   # Ligne
COLS = 8   # Colonne
WALL = 0   # Mur
CAVERN = 1 # Caverne 
CORRIDOR = 2 # Corridor
NB_WELL = 2 # Nombre puit 

# Nombres des cavernes, corridors et chauves-souris selon les niveau
PARAMS = {
    "easy":   {"nb_caverns": 16, "nb_corridors": 8,  "nb_bat": 1}, 
    "medium": {"nb_caverns": 12, "nb_corridors": 14, "nb_bat": 2},
    "hard":   {"nb_caverns": 8,  "nb_corridors": 20, "nb_bat": 2},
}

# Tuples qui gère les directions selon les direction cardinales 
DIRS    = [(-1, 0, "n"), (0, 1, "e"), (1, 0, "s"), (0, -1, "w")]
DIR_MAP = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
OPP     = {"n": "s", "s": "n", "e": "w", "w": "e"}

# Type de tuile et on lui associe les directions ouvertes (frozenset est utilisé comme un set!)
TILE_DIRS = {
    1: frozenset(["n", "e"]),  # hallne
    2: frozenset(["n", "w"]),  # hallnw
    3: frozenset(["s", "e"]),  # hallse
    4: frozenset(["s", "w"]),  # hallsw
}

# Associe un identifiant de tuile à un nom (sprites)
TILE_NAME = {
    0: "roombase",
    1: "hallne",
    2: "hallnw",
    3: "hallse",
    4: "hallsw",
}

# Fonction Wrap sert que si on dépasse les bords de la map tu reviens de l'autres côtés 
def _wrap(r, c):
    return r % ROWS, c % COLS

# Fonction dir_vec converti une lettre de direction en vecteur de déplacement 
def _dir_vec(l):
    return next((dr, dc) for dr, dc, ll in DIRS if ll == l)

# Fonction qui détermine où le personnage se déplace réellement applique aussi les fonctions précèdente 
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

# Fonction qui explore toute les cases accessbiles depuis le start du jeu (position de départ)
def _bfs_caverns(tiles, start):
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

# Fonction qui vérifie si toutes les cases  sont connecté entre elles
def _all_connected(tiles):
    cavernes = [(r, c) for r in range(ROWS) for c in range(COLS) if tiles[r][c] == 0]
    if not cavernes:
        return False
    return len(_bfs_caverns(tiles, cavernes[0])) == len(cavernes)

# Fonction qui génère complètement les corridors en respectants les contraintes de connexions 
def _generate_full_grid():
    tiles = [[0] * COLS for _ in range(ROWS)]

    for r in range(ROWS):
        for c in range(COLS):
            # Contraintes Nord
            if r > 0:
                north_neighbor = tiles[r-1][c]
                must_have_north = "s" in TILE_DIRS.get(north_neighbor, set())
                forbid_north  = "s" not in TILE_DIRS.get(north_neighbor, set())
            else:
                must_have_north = False
                forbid_north = True  # Bord haut pas d'ouverture Nord

            # Contraintes Ouest
            if c > 0:
                west_neighbor   = tiles[r][c-1]
                must_have_west= "e" in TILE_DIRS.get(west_neighbor, set())
                forbid_west = "e" not in TILE_DIRS.get(west_neighbor, set())
            else:
                must_have_west = False
                forbid_west   = True  # Bord gauche pas d'ouverture Ouest

            # Bord droit  pas d'ouverture Est
            forbid_east= (c == COLS - 1)
            # Bord bas  pas d'ouverture Sud
            forbid_south = (r == ROWS - 1)

            compatibles = []
            for t, dirs in TILE_DIRS.items():
                if must_have_north and "n" not in dirs: continue
                if must_have_west and "w" not in dirs: continue
                if forbid_north   and "n" in dirs:     continue
                if forbid_west  and "w" in dirs:     continue
                if forbid_east   and "e" in dirs:     continue
                if forbid_south   and "s" in dirs:     continue
                compatibles.append(t)

            # Si pas de compatibles grille invalide
            if not compatibles:
                return None

            tiles[r][c] = random.choice(compatibles)

    return tiles

# Fonction qui gènére une grille jouables avec un nombres de corridors et cavernes connectées 
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

        if _all_connected(tiles):
            return tiles

    return tiles

#  Fonction qui vérifie si une direction est accessibles depuis une case données
def _is_passable(tiles, r, c, direction):
    t = tiles[r][c]
    if t == 0:
        return True
    return direction.lower() in TILE_DIRS[t]

# Fonction qui calcule la distance (en déplacments) entre deux cavernes avec 
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

# Fonction qui place le joueur, le wumpus, les puits et les chauves-souris sur la grille
def _place_entities(tiles, nb_puits, nb_chauves):
    cavernes = [(r, c) for r in range(ROWS) for c in range(COLS) if tiles[r][c] == 0]
    random.shuffle(cavernes)
    idx = 0

    ent = {
        "wumpus": None, "well": [], "bat": [],
        "player": None, "foam": set(), "red": set()
    }

    ent["wumpus"]  = cavernes[idx]; idx += 1
    ent["well"]   = [cavernes[idx + i] for i in range(nb_puits)]; idx += nb_puits
    ent["bat"] = [cavernes[idx + i] for i in range(nb_chauves)]; idx += nb_chauves

    # Mousse dans les cavernes adjacentes aux puits (jamais sur un puits)
    for pr, pc in ent["well"]:
        for _, _, l in DIRS:
            dest = _move_destination(tiles, pr, pc, l)
            if list(dest) not in ent["puits"]:
                ent["foam"].add(dest)

    # Rouge dans les cavernes à distance <= 2 du wumpus
    wr, wc = ent["wumpus"]
    for r in range(ROWS):
        for c in range(COLS):
            if tiles[r][c] == 0 and (r, c) != (wr, wc):
                if _dist_cav(tiles, wr, wc, r, c) <= 2:
                    ent["red"].add((r, c))

    # Joueur placé dans une caverne sûre (ni puits, ni wumpus, ni mousse)
    interdits = set(ent["well"]) | {ent["wumpus"]} | ent["foam"]
    for pos in cavernes[idx:]:
        if pos not in interdits:
            ent["player"] = pos
            break

    return ent

# Fonction qui détermine le sprite à afficher pour une case selon son contenu et ses voisins
def _bg_img(tiles, r, c, puits_s, mousse_s, rouge_s):
    t = tiles[r][c]
    if t != 0:
        # Vérifie si on forme un S avec le voisin de droite
        if t == 1 and c + 1 < COLS:  # hallne + hallsw à droite hallnesw
            if tiles[r][c+1] == 4:
                return "hallnesw"
        if t == 2 and c + 1 < COLS:  # hallnw + hallse à droite hallnwse
            if tiles[r][c+1] == 3:
                return "hallnwse"
        # Vérifie si on est la case droite d'un S (on affiche rien de spécial)
        if t == 4 and c - 1 >= 0:  # hallsw précédé de hallne
            if tiles[r][c-1] == 1:
                return "hallnesw"
        if t == 3 and c - 1 >= 0:  # hallse précédé de hallnw
            if tiles[r][c-1] == 2:
                return "hallnwse"
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

# Fonction qui construit une grille exploitable pour l'affichage avec toutes les infos nécessaires 
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

# Fonction qui transforme l'état du jeu en grille affichable 
def get_grid(state):
    tiles     = state["tiles"]
    wumpus_t  = tuple(state["wumpus"])
    puits_s   = set(map(tuple, state["well"]))
    chauves_s = set(map(tuple, state["bat"]))
    mousse_s  = set(map(tuple, state["foam"]))
    rouge_s   = set(map(tuple, state["red"]))
    return _build_grid(tiles, wumpus_t, puits_s, chauves_s, mousse_s, rouge_s)

# Fonction qui calcule les perceptions du joueur(odeur, vents) => se sont les messages affiché si on se rapproche de quelque choses
def _calc_percepts(state):
    pos = (state["player"]["y"], state["player"]["x"])
    p   = []
    if pos in set(map(tuple, state["red"])):
        p.append("stench")
    if pos in set(map(tuple, state["foam"])):
        p.append("breeze")
    return p

# Fonction qui initilise une nouvelle partie avec tout les éléments du jeu selon le choix de la difficulté et du mode 
def new_game_state(difficulty="easy", mode="normal", vision="normal"):
    p      = PARAMS.get(difficulty, PARAMS["easy"])
    tiles  = _generate(p["nb_corridors"])
    ent    = _place_entities(tiles, NB_WELL, p["nb_bat"])
    jr, jc = ent["player"]

    map = [[CAVERN if tiles[r][c] == 0 else CORRIDOR for c in range(COLS)]
             for r in range(ROWS)]

    state = {
        "h": ROWS,
        "w": COLS,
        "difficulty": difficulty,
        "mode": mode,
        "vision": vision,
        "tiles": tiles,
        "map": map,
        "wumpus": list(ent["wumpus"]),
        "well": [list(p) for p in ent["well"]],
        "bat": [list(b) for b in ent["bat"]],
        "foam": [list(m) for m in ent["foam"]],
        "red": [list(r) for r in ent["red"]],
        "player": {"y": jr, "x": jc},
        "last_dir": "S",
        "reveals": [[True] * COLS for _ in range(ROWS)],
        "game_over": False,
        "result": None,
        "percepts": [],
        "has_arrow": True,
    }
    state["percepts"] = _calc_percepts(state)
    return state

# Fonction qui détermine si une case est vissible selon le mode de vision 
def cell_is_visible(state, x, y):
    if state["vision"] == "blind":
        return state["player"]["x"] == x and state["player"]["y"] == y
    return state["revele"][y][x]

# Fonction qui contrimé au déplacement du joueur et gère les collision et morts 
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
        state["reveals"][r2][c2] = True
        r2, c2 = _wrap(r2 + dr, c2 + dc)

    state["player"]["y"] = ny
    state["player"]["x"] = nx
    state["last_dir"] = direction
    state["reveals"][ny][nx] = True

    if [ny, nx] in state["well"]:
        state["game_over"] = True
        state["result"] = "dead_slime"
        _reveal_all(state)
        return state

    if [ny, nx] == state["wumpus"]:
        state["game_over"] = True
        state["result"] = "dead_wumpus"
        _reveal_all(state)
        return state

    state = _check_bat(state, ny, nx)
    if not state["game_over"]:
        state["percepts"] = _calc_percepts(state)
    return state

# Fonction qui gère la téléportation du joueur en cas de rencontre avec une chauve-souris
def _check_bat(state, r, c):
    if [r, c] not in state["bat"]:
        return state

    tiles = state["tiles"]
    interdits = [state["wumpus"]] + state["well"]
    libre = [
        [row, col] for row in range(ROWS) for col in range(COLS)
        if tiles[row][col] == 0
        and [row, col] not in interdits
        and [row, col] != [r, c]
    ]

    if not libre:
        return state

    # Téléportation dès la 1ère visite
    dest = random.choice(libre)
    state["player"]["y"] = dest[0]
    state["player"]["x"] = dest[1]
    state["reveals"][dest[0]][dest[1]] = True

    autres = [p for p in libre if p != dest]
    if autres:
        i = state["bat"].index([r, c])
        state["bat"][i] = random.choice(autres)

    if dest in state["well"]:
        state["game_over"] = True
        state["result"]    = "dead_slime"
        _reveal_all(state)
    elif dest == state["wumpus"]:
        state["game_over"] = True
        state["result"]    = "dead_wumpus"
        _reveal_all(state)

    return state

# Fonction qui va gèrer le tir de la flèche et qui va déterminé si le wumpus va être touché ou non 
def shoot_arrow(state, direction):
    if state["game_over"] or not state["has_arrow"]:
        return state

    state["has_arrow"] = False
    dl = direction.lower()
    tiles = state["tiles"]
    py, px = state["player"]["y"], state["player"]["x"]
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

# Fonction qui révèle toute la carte (fin de la partie !)
def _reveal_all(state):
    state["reveals"] = [[True] * COLS for _ in range(ROWS)]