from app import db

class Announce(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(150))
    content = db.Column(db.String(250), nullable=False)


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine,text
from flask import Flask
from config import Config
from random import randint


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
connection = engine.connect()
random_id = randint(000, 999)

class teaching(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    class_teaching = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(150))
    
    
    


