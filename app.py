#! /usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("homeScreen.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pseudo = request.form.get("pseudo")
        password = request.form.get("password")

        print("Pseudo :", pseudo)
        print("Password :", password)

        return redirect(url_for("home"))

    return render_template("login.html")

@app.route("/classement")
def classement():
    return render_template("classement.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

if __name__ == "__main__":
    app.run(debug=True)
