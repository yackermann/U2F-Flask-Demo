from app import db

class Auth(db.Model):
    __tablename__ = 'users'

    id       = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(70))

    def __init__(self, name=None, password=None):
        self.name = name
        self.password = password

    def __repr__(self):
        return '<User %r>' % (self.name)