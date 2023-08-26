from setup import app
from flask import render_template
from db_model import User


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
    users = User.query.all()
    scores = []
    for user in users:
        scores.append({
                "username": user.username,
                "score": user.high_score
            })
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)
    return render_template('scores.html', scores=scores)
