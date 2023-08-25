from setup import app
from flask import render_template


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/register")
def register():
    return render_template('register.html')


@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/quiz")
def quiz():
    return render_template('quiz.html')


@app.route("/scores")
def scores():
    return render_template('scores.html')
