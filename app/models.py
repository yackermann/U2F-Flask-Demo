from app import db
from sqlalchemy.sql.expression import select, exists

class Auth(db.Model):
    __tablename__ = 'users'

    id       = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % (self.username)

    def exists(self):
        return db.session.query(exists().where(Auth.username == self.username)).scalar()
