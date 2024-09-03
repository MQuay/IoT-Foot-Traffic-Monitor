from os import environ

class Prod:
    """Set Flask configuration from .env file."""

    # Database
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}".format(
        username=environ.get("RDS_USERNAME"),
        password=environ.get("RDS_PASSWORD"),
        host=environ.get("RDS_HOSTNAME"),
        port=environ.get("RDS_PORT"),
        database=environ.get("RDS_DB_NAME")
    )
    SECRET_KEY = environ.get("SECRET_KEY")

class Dev(object):
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://mquay@localhost/project-webtest"
    SECRET_KEY = "SECRET_KEY"