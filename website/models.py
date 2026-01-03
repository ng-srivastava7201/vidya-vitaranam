from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(150), unique=True)
  email = db.Column(db.String(150))
  password = db.Column(db.String(150))
  name = db.Column(db.String(150))
  school = db.Column(db.String(150))
  role = db.Column(db.String(10), default='student')

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100))
    chapter = db.Column(db.String(100))
    filename = db.Column(db.String(200))   
    youtube_link = db.Column(db.String(300))
    teacher_name = db.Column(db.String(150))
    upload_date = db.Column(db.DateTime(timezone=True), default=func.now())
