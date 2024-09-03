from flask import Blueprint, make_response, jsonify, request, redirect, flash, render_template
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import func
from app.models import db, Device, Log
from datetime import datetime
import requests
from os import environ

jwt = JWTManager()
crypt = Bcrypt()
api = Blueprint('api', __name__)
web_url = "https://" # url of the web/cloud application

class JWTtokens():
    admin_token = ""

    def get_token(self):
        res = requests.post(web_url + "/login", json={"device_name":"admin", "password":environ.get("PW")})
        self.admin_token = res.text[1:len(res.text)-2]
        #print("TOKEN:  " + str(self.admin_token) + "\n\n")
        #print(res.text + "\n" + self.admin_token)
        return

t = JWTtokens()

# https://flask-jwt-extended.readthedocs.io/en/latest/automatic_user_loading.html
# Register a callback function that takes whatever object is passed in as the
# identity when creating JWTs and converts it to a JSON serializable format.
@jwt.user_identity_loader
def user_identity_lookup(device):
    return device.id

# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return db.session.execute(db.select(Device.id).where(Device.id == identity)).scalar_one_or_none()

@api.route('/pong')
def pong():
    #t.get_token()
    return make_response("hello there")
"""
    incoming json:
    {
        "device_name": str,
    }
"""
@api.route('/add-device', methods=['GET', 'POST'])
def add_device():
    name = request.json.get("device_name")
    d = db.session.execute(db.select(Device.id, Device.device_name, Device.password).where(Device.device_name == name)).one_or_none()
    if d:
        return jsonify("already added")
    # add device to web app via API call to /add-device
    while t.admin_token == "":
        t.get_token()
    
    device = Device(device_name = name)
    password = device.gen_password()
    res = requests.post(web_url + "/add-device", headers={"Authorization":"Bearer " + t.admin_token}, json={"device_name":name, "password":password})
    if "Done" in res.text:
        device.password = crypt.generate_password_hash(password).decode("utf-8")
        db.session.add(device)
        db.session.commit()
        return jsonify(password)
    else:
        return jsonify("failed to add")

"""
    incoming json:
    {
        "device_name": str,
        "password": str
    }
"""
# login            Adapted from docs at: https://flask-jwt-extended.readthedocs.io/en/stable/automatic_user_loading.html
@api.route('/login', methods=['POST'])
def login():
    name = request.json.get("device_name", None)
    pw = request.json.get("password", None)
    print(name)
    print(pw)
    d = db.session.execute(db.select(Device.id, Device.device_name, Device.password).where(Device.device_name == name)).one_or_none()
    if d and crypt.check_password_hash(d.password, pw):
        db.session.execute(db.update(Device).where(Device.id == d.id).values(last_login = func.now()))
        access_token = create_access_token(identity=d)
        return jsonify(access_token=access_token)
    else:
        return jsonify("Incorrect device name or password"), 401

# TODO: get all logs, display somewhat pretty-ish
@api.route('/logs', methods=['GET'])
@jwt_required()
def get_logs():
    logs = db.session.execute(db.select(Log).order_by(Log.timestamp)).scalars()
    result = logs.all()
    json_response = jsonify([x.todict() for x in result])
    response = make_response(json_response)
    return response

@api.route('/devices', methods=['GET'])
@jwt_required()
def device_list():
    devices = db.session.execute(db.select(Device).order_by(Device.id)).scalars()
    result = devices.all()
    json_response = jsonify([x.todict() for x in result])
    response = make_response(json_response)
    return response

# @routes.route('/refresh', methods=['POST'])
# def refresh_token():
#     pass

@api.route('/alarm', methods=['GET', 'POST'])
#@jwt_required()
def alarm():
    alert_string = "Device: onetwothreed    |    Timestamp: " + str(datetime.now())
    flash(alert_string)
    return ("Ack")

@api.route("/intrusions", methods=['GET'])
def intrusions():
    return render_template('intrusion-list.html')

# TODO: API call to web app to edit options
def change_opt(alarm, logging):
    req = {}
    req["alarm"] = alarm
    if alarm:
        req["logging"] = True
    else:
        req["logging"] = logging
    while t.admin_token == "":
        t.get_token()
    res = requests.post(web_url + "/options", headers={"Authorization":"Bearer " + t.admin_token}, json = req)
    return

# @api.route("/reset", methods=['GET', 'POST'])
# def resetDB():
#     while t.admin_token == "":
#         t.get_token()
#     print("got token")
#     res = requests.post(web_url + "/reset", headers={"Authorization":"Bearer " + t.admin_token})
#     print("did the request")
#     if "Done" in res.text:
#         db.drop_all()
#         db.create_all()
#     else:
#         return ("Failed to reset\nResponse from server:\n" + res.text)


"""
    no json body?
    incoming json:
    {
        
    }
"""
# @routes.route('/sense', methods=['POST'])
# @jwt_required()
# def sensed():
#     if opt.get_alarm:
#         create_alert()
#         d_id = current_user.id
#         db.session.add(Log(device_id = d_id, status = "INTRUSION"))
#         db.session.commit()
#         return jsonify("ALARM TRIPPED")
#     elif opt.get_logging:
#         d_id = current_user.id
#         db.session.add(Log(device_id = d_id, status = "Normal"))
#         db.session.commit()
#         return jsonify("Done")


# @routes.route('/monitor-options', methods=['GET', 'POST'])
# @jwt_required
# def alarm_options():
#     if check_admin(current_user, request.json.get("password")):
#         set = request.json.get("options")
#         if "Alarm" in set:
#             opt.set_alarm(set["Alarm"])
#         elif "Logging" in set:
#             opt.set_logging(set["Logging"])
#         return jsonify("Settings changed. New settings:\n" + str(MONITOR_OPTIONS))
#     else:
#         return jsonify("Forbidden"), 403

