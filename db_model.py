from setup import db
from datetime import datetime


class User(db.Model):

    __tablename__ = 'User'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    uuid = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String)
    registration_date = db.Column(db.String)
    acceptable_token_creation_date = db.Column(db.String)
    answered_questions = db.Column(db.String)
    last_generated_question = db.Column(db.Integer)
    score = db.Column(db.Integer)
    high_score = db.Column(db.Integer)

    def __init__(
        self, uuid, username, email, password, answered_questions,
        last_generated_question, score, high_score
    ):
        self.uuid = uuid
        self.username = username
        self.email = email
        self.password = password
        self.registration_date = str(datetime.today())
        self.acceptable_token_creation_date = str(datetime.today())
        self.answered_questions = answered_questions
        self.last_generated_question = last_generated_question
        self.score = score
        self.high_score = high_score
