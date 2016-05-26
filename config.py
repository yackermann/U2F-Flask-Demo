import os
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE    = 'flaskr.db'
DEBUG       = True
USERNAME    = 'admin'
PASSWORD    = 'admin'
APPID       = 'https://localhost:5000'
COOKEY_FILE = 'COOKEY.key'

with open(COOKEY_FILE) as r:
    SECRET_KEY = r.read() #Reads key from file

# TODO -> Implement facets support
# APPID       = 'https://localhost:5000/facets.json'

# defines the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# the database uri
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
SQLALCHEMY_TRACK_MODIFICATIONS = False