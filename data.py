
from google.appengine.ext import db


class Page(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class User(db.Model):
    name = db.StringProperty(required=True)
    password = db.TextProperty(required=True)
    email = db.StringProperty()
