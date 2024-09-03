from flask import Flask
from app.config import Dev, Prod
from app.models import db, Base, Device, Log
from app.routes import jwt, crypt, api, t
import random
from os import environ

def create_app():
    app = Flask(__name__)
    if "RDS_USERNAME" in environ:
        app.config.from_object(Prod)
    else:
        app.config.from_object(Dev)
    #register_extensions(application)
    db.init_app(app)
    crypt.init_app(app)
    jwt.init_app(app)
    app.register_blueprint(api)

    with app.app_context():
        db.drop_all()
        db.create_all()
        # if 0:
        #     create_dummy()
        d = Device(
            device_name = "admin",
            password = crypt.generate_password_hash(environ.get("SECRET_KEY")).decode("utf-8")
        )
        db.session.add(d)
        db.session.commit()
    return app


# def create_dummy():
#     for i in range(5):
#         n = random.randint(0, 999)
#         d = Device(
#             id = n,
#             device_name = "device" + str(n)
#         )
#         db.session.add(d)
#         db.session.commit()


# def register_extensions(app):
#     db.init_app(application)
#     crypt.init_app(application)
#     jwt.init_app(application)
#     application.register_blueprint(api)