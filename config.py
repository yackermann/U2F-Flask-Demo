import os
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE    = 'flaskr.db'
DEBUG       = True
SECRET_KEY  = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
USERNAME    = 'admin'
PASSWORD    = 'admin'
APPID       = 'http://localhost:5000/'

# defines the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# the database uri
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH