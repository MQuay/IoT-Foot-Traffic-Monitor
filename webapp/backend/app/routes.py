from flask import Blueprint, make_response, jsonify, request, redirect, flash, render_template
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, get_jwt_identity, jwt_required, current_user
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import func
from app.models import db, Device, Log
from datetime import datetime
import requests

jwt = JWTManager()
crypt = Bcrypt()
api = Blueprint('api', __name__)
local_url=""

class JWTtokens():
    admin_token = ""

    def get_token(self):
        res = requests.post(web_url + "/login", json={"device_name":"admin", "password":"supersecret"})
        self.admin_token = res.json()['access_token']
        print("TOKEN:  " + str(self.admin_token) + "\n\n")
        return

t = JWTtokens()

class MonitorSettings():
    _OPTIONS = {"Alarm": True, "Logging": True}
    
    def get_alarm(self):
        return self._OPTIONS["Alarm"]

    def get_logging(self):
        return self._OPTIONS["Alarm"]

    def set_alarm(self, b):
        if b:
            self._OPTIONS["Alarm"] = b
            self._OPTIONS["Logging"] = True
        else:
            self._OPTIONS["Alarm"] = b

    def set_monitor(self, b):
        if not b:
            self._OPTIONS["Alarm"] = False
            self._OPTIONS["Logging"] = b
        else:
            self._OPTIONS["Logging"] = b

opt = MonitorSettings()

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
    return db.session.execute(db.select(Device).where(Device.id == identity)).scalar_one_or_none()

@api.route('/', methods=['GET'])
def hello():
    return jsonify("hello there")

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
    d = db.session.execute(db.select(Device.id, Device.device_name, Device.password).where(Device.device_name == name)).one_or_none()
    if d and crypt.check_password_hash(d.password, pw):
        db.session.execute(db.update(Device).where(Device.id == d.id).values(last_login = func.now()))
        access_token = create_access_token(identity=d)
        return jsonify(access_token)
    else:
        return jsonify("Incorrect device name or password"), 401

@api.route('/sense', methods=['GET', 'POST'])
@jwt_required()
def sensed():
    if opt.get_alarm:
        d_id = current_user.id
        db.session.add(Log(device_id = d_id, status = "INTRUSION"))
        db.session.commit()
        # alarm_site()
        return jsonify("ALARM TRIPPED")
    elif opt.get_logging:
        d_id = current_user.id
        db.session.add(Log(device_id = d_id, status = "Normal"))
        db.session.commit()
        return jsonify("Done")

@api.route("/intrusions", methods=['GET'])
#@jwt_required()
def intrusions():
    return render_template('intrusion-list.html', messages=get_intrusions())

def get_intrusions():
    intr = []
    q = db.session.execute(db.select(Log).order_by(Log.timestamp)).scalars()
    result = q.all()
    logs = [x.todict() for x in result]
    for log in logs:
        if log["status"] == "INTRUSION":
            d = db.session.execute(db.select(Device.device_name).where(Device.id == log["device_id"])).scalar_one_or_none()
            log_str = "ID: " + str(log["id"]) + "    |    Device: " + d + "   |    Timestamp: " + str(log["timestamp"])
            intr.append(log_str)
    return intr

# def alarm_site():
#     while t.admin_token == "":
#         t.get_token()
#     res = requests.post(local_url + "/alarm-from-web", headers = {"Authorization": "Bearer " + t.admin_token})
#     print(res.text)

"""
    incoming json:

    {
        "password": str,
        "Alarm": bool,
        "Logging": bool
    }
"""
@api.route('/options', methods=['GET', 'POST'])
@jwt_required()
def alarm_options():
    if current_user.device_name == "admin":
        alarm = request.json.get("alarm")
        logging = request.json.get("logging")
        if alarm:
            opt.set_alarm(alarm)
        elif logging:
            opt.set_logging(logging)
        return jsonify("Settings changed. New settings:\n" + str(MONITOR_OPTIONS))
    else:
        return jsonify("Forbidden"), 403

"""
    incoming json:
    {
        "device_name": str,
        "password": str
    }
"""
@api.route('/add-device', methods=['POST'])
@jwt_required()
def add_device():
    if current_user.device_name == "admin":
        name = request.json.get("device_name")
        pw = request.json.get("password")
        d = db.session.execute(db.select(Device).where(Device.device_name == name)).one_or_none()
        if d:
            return jsonify("Device name already exists")
        else:    
            device = Device(
                device_name = name,
                password = crypt.generate_password_hash(pw).decode("utf-8"),
                last_login=datetime(1970, 1, 1))
            db.session.add(device)
            db.session.commit()
            return jsonify("Done")
    else:
        return jsonify("Forbidden"), 403

# @api.route('/reset', methods=['POST'])
# @jwt_required()
# def resetDB():
#     if current_user.device_name == "admin":
#         db.drop_all()
#         db.create_all()
#         return ("Done")
#     else:
#         return jsonify("Forbidden"), 403


# TODO ping server periodically
# @routes.route('/ping', methods=['POST'])
# @jwt_required()
# def ping():
#     pass