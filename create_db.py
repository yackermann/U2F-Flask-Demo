from config import SQLALCHEMY_DATABASE_URI
from app import db
from app import models
import os.path

# create the database and the db table
db.create_all()

# commit the changes
db.session.commit()