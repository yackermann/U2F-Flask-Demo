from app import db, passwords
from sqlalchemy.sql.expression import select, exists
# from passwords import hash_password, check_password 

class Auth(db.Model):
    __tablename__ = 'users'

    id       = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)

    def __init__(self, username, password=None):
        self.username = username

        if password:
            self.password = passwords.hash_password(password)

    def __repr__(self):
        return '<User %r>' % (self.username)

    def set_password(self, password):
        """Generate a random salt and return a new hash for the password."""
        self.password = passwords.hash_password(password)


    def check_password(self, password):
        """Check a password against an existing hash."""
        return passwords.check_password(self.password, password)
