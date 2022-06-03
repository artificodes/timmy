import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = "postgresql://postgres:admin@localhost:5432/fyyur"


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    # SQLALCHEMY_DATABASE_URI = "postgresql://{username}:{password}@localhost:5432/{dbname}"


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
