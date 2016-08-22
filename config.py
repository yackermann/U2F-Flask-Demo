import os, logging

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
U2F_FACETS_ENABLED = True
U2F_FACETS_LIST    = [
    'https://u2f.jeman.de',
    'https://secure.jeman.de'
]
# ----- U2F ENDS ----- #



# ----- DATABASES ----- #
DATABASE    = 'flaskr.db'
USERNAME    = 'admin'
PASSWORD    = 'admin'

# defines the full path for the database
BASEDIR       = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASEDIR, DATABASE)

# the database uri
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
SQLALCHEMY_TRACK_MODIFICATIONS = False
# ----- DATABASES ENDS ----- #