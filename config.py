from settings import DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME
import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@localhost:5432/{}'.format(DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME)
SQLALCHEMY_TRACK_MODIFICATIONS = False

