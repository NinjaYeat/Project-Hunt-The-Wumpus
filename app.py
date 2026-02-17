#! /usr/bin/env python3
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("homeScreen.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/classement")
def classement():
    return render_template("classement.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

if __name__ == "__main__":
    app.run(debug=True)
