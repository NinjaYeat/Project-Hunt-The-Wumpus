#! /usr/bin/env python3
#! Amine Isenborghts et Nora Lfarh

import os
import secrets
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_conn
from wumpus_map import new_game_state, move_player, cell_is_visible

from psycopg.rows import dict_row

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me-now")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("FLASK_COOKIE_SECURE", "0") == "1",
)


def current_user_id():
    return session.get("user_id")


def _ensure_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)


def _check_csrf():
    token_form = request.form.get("csrf_token", "")
    token_sess = session.get("csrf_token", "")
    return bool(token_form and token_sess and token_form == token_sess)


@app.context_processor
def inject_csrf():
    _ensure_csrf_token()

    def csrf_token():
        return session.get("csrf_token", "")

    return {"csrf_token": csrf_token}

@app.context_processor
def inject_helpers():
    return {"cell_is_visible": cell_is_visible}

@app.route("/")
def home():
    return render_template("homeScreen.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    _ensure_csrf_token()

    if request.method == "POST":
        if not _check_csrf():
            flash("Requête invalide (CSRF). Réessaie.")
            return redirect(url_for("register"))

        username = request.form.get("pseudo", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Le pseudo et le mot de passe ne peuvent pas être vides.")
            return redirect(url_for("register"))

        if len(username) < 5 or len(username) > 10:
            flash("Le pseudo doit etre entre 5 et 10 caractères.")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Le mot de passe doit faire au moins 6 caractères.")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
                    if cur.fetchone():
                        flash("Ce pseudo est déjà utilisé.")
                        return redirect(url_for("register"))

                    cur.execute(
                        "INSERT INTO users (username, password_hash) VALUES (%s, %s);",
                        (username, password_hash),
                    )

            flash("Compte créé. Connecte-toi maintenant.")
            return redirect(url_for("login"))
        except Exception:
            app.logger.exception("Erreur register")
            flash("Erreur serveur lors de la création du compte.")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    _ensure_csrf_token()

    if request.method == "POST":
        if not _check_csrf():
            flash("Requête invalide (CSRF). Réessaie.")
            return redirect(url_for("login"))

        username = request.form.get("pseudo", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Le pseudo et le mot de passe ne peuvent pas être vides.")
            return redirect(url_for("login"))

        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, username, password_hash FROM users WHERE username = %s;",
                        (username,),
                    )
                    row = cur.fetchone()

            if (not row) or (not check_password_hash(row["password_hash"], password)):
                flash("Pseudo ou mot de passe incorrect.")
                return redirect(url_for("login"))

            session.clear()
            _ensure_csrf_token()
            session["user_id"] = row["id"]
            session["username"] = row["username"]
            return redirect(url_for("menu"))
        except Exception:
            app.logger.exception("Erreur login")
            flash("Erreur serveur lors de la connexion.")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/menu", methods=["GET", "POST"])
def menu():
    if not current_user_id():
        return redirect(url_for("login"))

    _ensure_csrf_token()

    if request.method == "POST":
        if not _check_csrf():
            flash("Requête invalide (CSRF). Réessaie.")
            return redirect(url_for("menu"))

        difficulty = request.form.get("difficulty", "easy")
        mode = request.form.get("mode", "normal")
        vision = request.form.get("vision", "normal")

        if difficulty not in ("easy", "medium", "hard"):
            difficulty = "easy"
        if mode not in ("normal", "express"):
            mode = "normal"
        if vision not in ("normal", "blind"):
            vision = "normal"

        session["difficulty"] = difficulty
        session["mode"] = mode
        session["vision"] = vision

        state = new_game_state(difficulty=difficulty, mode=mode, vision=vision)
        session["game_state"] = state

        return redirect(url_for("game"))

    return render_template("menu.html")


@app.route("/game")
def game():
    if not current_user_id():
        return redirect(url_for("login"))

    state = session.get("game_state")
    if not state:
        state = new_game_state(
            difficulty=session.get("difficulty", "easy"),
            mode=session.get("mode", "normal"),
            vision=session.get("vision", "normal"),
        )
        session["game_state"] = state

    return render_template("game.html", state=state)


@app.route("/new_game", methods=["POST"])
def new_game():
    if not current_user_id():
        return redirect(url_for("login"))

    if not _check_csrf():
        flash("Requête invalide (CSRF). Réessaie.")
        return redirect(url_for("menu"))

    state = new_game_state(
        difficulty=session.get("difficulty", "easy"),
        mode=session.get("mode", "normal"),
        vision=session.get("vision", "normal"),
    )
    session["game_state"] = state
    return redirect(url_for("game"))


@app.route("/move", methods=["POST"])
def move():
    if not current_user_id():
        return redirect(url_for("login"))

    if not _check_csrf():
        flash("Requête invalide (CSRF). Réessaie.")
        return redirect(url_for("game"))

    state = session.get("game_state")
    if not state:
        return redirect(url_for("menu"))

    direction = request.form.get("dir", "")
    state = move_player(state, direction)
    session["game_state"] = state

    if state.get("game_over"):
        res = state.get("result")
        if res == "win":
            flash("Bravo ! Tu as trouvé l'or. C'est gagné !!!")
        elif res == "dead_wumpus":
            flash("Tu es tombé sur le Wumpus. Perdu")
        elif res == "dead_slime":
            flash("Tu es tombé dans le slime. Perdu")

    return redirect(url_for("game"))
@app.route("/finish_game", methods=["POST"])
def finish_game():
    if not current_user_id():
        return redirect(url_for("login"))

    if not _check_csrf():
        flash("Requête invalide (CSRF). Réessaie.")
        return redirect(url_for("game"))

    state = session.get("game_state")
    if not state or not state.get("game_over"):
        flash("Partie non terminée.")
        return redirect(url_for("game"))

    result = state.get("result")
    if result not in ("win", "dead_wumpus", "dead_slime"):
        flash("Résultat invalide.")
        return redirect(url_for("game"))

    user_id = session["user_id"]

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                if result == "win":
                    cur.execute("UPDATE users SET wins = wins + 1 WHERE id = %s;", (user_id,))
                elif result == "dead_wumpus":
                    cur.execute("UPDATE users SET died_wumpus = died_wumpus + 1 WHERE id = %s;", (user_id,))
                elif result == "dead_slime":
                    cur.execute("UPDATE users SET died_slime = died_slime + 1 WHERE id = %s;", (user_id,))

        session.pop("game_state", None)

    except Exception:
        app.logger.exception("Erreur finish_game")
        flash("Erreur serveur lors de l'enregistrement du résultat.")
        return redirect(url_for("game"))

    return redirect(url_for("classement"))

@app.route("/classement")
def classement():
    if not current_user_id():
        return redirect(url_for("login"))

    slots = [
        {"username": "Nora", "wins": 0},
        {"username": "Yanis", "wins": 0},
        {"username": "Amine", "wins": 0},
    ]

    try:
        with get_conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT username, wins
                    FROM users
                    ORDER BY wins DESC, username ASC
                    LIMIT 3;
                """)
                rows = cur.fetchall()
        for i, r in enumerate(rows[:3]):
            slots[i] = r

    except Exception:
        app.logger.exception("Erreur classement")

    return render_template("classement.html", slots=slots)

@app.route("/settings")
def settings():
    if not current_user_id():
        return redirect(url_for("login"))
    return render_template("settings.html")

if __name__ == "__main__":
    app.run(debug=True)