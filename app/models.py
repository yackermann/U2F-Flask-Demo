from app import db, passwords
from sqlalchemy.sql.expression import select, exists
import json

class Auth(db.Model):
    __tablename__ = 'users'

    id          = db.Column(db.Integer, primary_key= True)
    username    = db.Column(db.String , unique=True)
    password    = db.Column(db.String)
    u2f_devices = db.Column(db.String)

    def __init__(self, username, password=None):
        self.username = username

        if password:
            self.password = passwords.hash_password(password)

        self.u2f_devices = json.dumps([])

    def __repr__(self):
        return '<User %r>' % (self.username)

    def commit(self):
        db.session.add(self)
        db.session.commit()

    # Password
    def set_password(self, password):
        """Generate a random salt and return a new hash for the password."""
        self.password = passwords.hash_password(password)

    def check_password(self, password):
        """Check a password against an existing hash."""
        return passwords.check_password(self.password, password)

    # U2F
    def get_u2f_devices(self):
        """Returns U2F devices"""
        return json.loads(self.u2f_devices)

    def set_u2f_devices(self, devices):
        """Saves U2F devices"""
        self.u2f_devices = json.dumps(devices)
