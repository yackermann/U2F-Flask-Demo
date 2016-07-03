from app import db, passwords
from sqlalchemy.sql.expression import select, exists
import json, logging

LOG_PREFIX = 'MODELS:'

class Auth(db.Model):
    __tablename__ = 'users'

    id          = db.Column(db.Integer, primary_key = True)
    username    = db.Column(db.String , unique      = True)
    password    = db.Column(db.String)
    u2f_devices = db.Column(db.String)

    def __init__(self, username, password = None):
        logging.debug('%s Adding new user with username: %s', LOG_PREFIX, username)
        self.username = username.lower()

        if password:
            logging.debug('%s Password provided', LOG_PREFIX, username)
            self.password = passwords.hash_password(password)

        self.u2f_devices = json.dumps([])

    def __repr__(self):
        return '<User %r>' % (self.username)

    def commit(self):
        logging.debug('%s Updating record of the user: %s', LOG_PREFIX, self.username)
        db.session.add(self)
        db.session.commit()

    # Password
    def set_password(self, password):
        """Generate a random salt and return a new hash for the password."""
        logging.debug('%s Setting new password for user: %s', LOG_PREFIX, self.username)
        self.password = passwords.hash_password(password)

    def check_password(self, password):
        """Check a password against an existing hash."""
        logging.debug('%s Checking %s\'s password', LOG_PREFIX, self.username)
        return passwords.check_password(self.password, password)

    # U2F
    def get_u2f_devices(self):
        """Returns U2F devices"""
        logging.debug('%s Retrieving %s\'s U2F devices', LOG_PREFIX, self.username)
        return json.loads(self.u2f_devices)

    def set_u2f_devices(self, devices):
        """Saves U2F devices"""
        logging.debug('%s Updating %s\'s U2F devices', LOG_PREFIX, self.username)
        self.u2f_devices = json.dumps(devices)

    def verify_u2f_counter(self, signature, counter):
        """Verifies U2F device counter"""
        devices = self.get_u2f_devices()
        logging.debug('%s Verifying %s\'s signature counter', LOG_PREFIX, self.username)
        for device in devices:
            # Searching for specific keyhandle
            if device['keyHandle'] == signature['keyHandle']:
                if counter > device['counter']:
                    # Updating counter record
                    logging.info('%s Verified counter for user: %s', LOG_PREFIX, self.username)
                    
                    device['counter'] = counter
                    self.set_u2f_devices(devices)
                    return True
                else:
                    logging.warning('%s Detected key clone. User: %s', LOG_PREFIX, self.username)
                    return False

        return False