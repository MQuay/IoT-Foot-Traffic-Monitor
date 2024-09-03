import os

class Prod:
    """Set Flask configuration from .env file."""

    # # General Config
    # ENVIRONMENT = environ.get(".env")

    # # Flask Config
    # FLASK_APP = "wsgi.py"
    # FLASK_DEBUG = environ.get("FLASK_DEBUG")
    # SECRET_KEY = environ.get("SECRET_KEY")

    # # Database
    # SQLALCHEMY_DATABASE_URI = environ.get("PROD_DATABASE_URI")
    # SQLALCHEMY_ECHO = False
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

class Dev(object):
    #ENVIRONMENT = os.environ.get(".env")
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://mquay@localhost/project-localtest"
    SECRET_KEY = os.environ.get("PW")
    #SQLALCEHMY_ENGINE_OPTIONS = {}