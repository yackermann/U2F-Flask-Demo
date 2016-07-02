import os
basedir = os.path.abspath(os.path.dirname(__file__))

# ----- APP Specific ----- #
DEBUG       = True
COOKEY_FILE = 'COOKEY.key'

with open(COOKEY_FILE) as r:
    SECRET_KEY = r.read() #Reads key from file
# ----- APP Specific ENDS ----- #


# ----- U2F ----- #
U2F_APPID               = 'https://localhost:5000'

# Uncomment to enable custom facets location
# U2F_CUSTOM_FACETS_APPID = 'https://localhost:5000/securutyKeys/facets.json'
U2F_CUSTOM_FACETS_APPID = ''
U2F_ENABLE_FACETS       = False
U2F_FACETS_LIST         = [
    'https://localhost:5000'
]


# Set appid to appid + /facets.json or custom location
if U2F_ENABLE_FACETS and not U2F_CUSTOM_FACETS_APPID:
    U2F_APPID += '/facets.json'
elif U2F_CUSTOM_FACETS_APPID:
    U2F_APPID = U2F_CUSTOM_FACETS_APPID
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