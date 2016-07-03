import os
basedir = os.path.abspath(os.path.dirname(__file__))
import logging

# ----- LOGGING ----- #
DEBUG     = True
LOG_FILE  = 'logfile.log'
# 1    DEBUG - detailed info
# 2     INFO - confirmation that things according to plan
# 3  WARNING - something unexpected
# 4    ERROR - some function failed
# 5 CRITICAL - application failure
LOG_LEVEL = logging.DEBUG

logging.basicConfig(filename = LOG_FILE, 
                    level    = LOG_LEVEL)
# Adds console print
logging.getLogger().addHandler(logging.StreamHandler())
# ----- LOGGING ENDS ----- #


# ----- COOKIE ----- #
COOKEY_FILE = 'COOKEY.key'

with open(COOKEY_FILE) as r:
    SECRET_KEY = r.read() #Reads key from file
# ----- COOKIE ENDS ----- #


# ----- U2F ----- #
U2F_APPID          = 'https://u2f.jeman.de'

# Set to True to enable facets
U2F_FACETS_ENABLED = False
U2F_FACETS_LIST    = [
    'https://u2f.jeman.de'
]


# Set appid to appid + /facets.json if U2F_FACETS_ENABLED
# or U2F_APP becomes U2F_FACETS_LIST
if U2F_FACETS_ENABLED:
    U2F_APPID += '/facets.json'
    assert len(U2F_FACETS_LIST) > 0
else:
    U2F_FACETS_LIST = [U2F_APPID]
# ----- U2F ENDS ----- #



# ----- DATABASES ----- #
DATABASE    = 'flaskr.db'
USERNAME    = 'admin'
PASSWORD    = 'admin'

# defines the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# the database uri
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
SQLALCHEMY_TRACK_MODIFICATIONS = False
# ----- DATABASES ENDS ----- #