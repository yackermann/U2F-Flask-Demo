from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy

from flask_fido_u2f import U2F

app = Flask(__name__)
app.config.from_object('config')
db  = SQLAlchemy(app)
u2f = U2F(app, enroll_route  = '/enroll'
             , sign_route    = '/sign'
             , devices_route = '/devices'
             , facets_route  = '/facets.json')

from app import static_routes, auth_routes
from app import models


@u2f.read
def read():
    user = models.Auth.query.filter_by(username=session['username']).first()
    return user.get_u2f_devices()

@u2f.save
def save(devices):
    user = models.Auth.query.filter_by(username=session['username']).first()
    user.set_u2f_devices(devices)
    user.commit()

@u2f.enroll_on_success
def enroll_on_success():
    # Executes on successful U2F enroll
    pass

@u2f.sign_on_success
def sign_on_success():
    session['logged_in'] = True
    u2f.enable_device_management()
    u2f.enable_enroll()