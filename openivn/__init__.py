"""OpenIVN package initializer script."""
import flask
import json
import os
import logging
from openivn.utilities.user import User
from flask_login import LoginManager
from oauthlib.oauth2 import WebApplicationClient
from threading import Thread
from openivn.utilities.listen_udp_msg import listen_udp_msg
from openivn.utilities.send_udp_msg import send_udp_msg
from openivn.utilities.listen_tcp_msg import listen_tcp_msg
from openivn.utilities.tcp_reverse_flow import tcp_reverse_flow

# Create app object to be used by all modules
app = flask.Flask(__name__)

# Import config settings
app.config.from_object('openivn.config')

# Use settings from environment variable, useful for different settings
# on development and production machines.
# See http://flask.pocoo.org/docs/config/ for more
app.config.from_envvar('OPENIVN_SETTINGS', silent=True)

# To fix:
# http://flask.pocoo.org/docs/patterns/packages/
# https://flask.palletsprojects.com/en/1.1.x/config/
# http://flask.palletsprojects.com/en/1.1.x/tutorial/install/

import openivn.api
import openivn.views
import openivn.model

# Google OAuth
GOOGLE_CLIENT_ID = (
    "INSERT_YOUR_OWN_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
)
GOOGLE_CLIENT_SECRET = "INSERT_YOUR_OWN_GOOGLE_CLIENT_SECRET"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Session management
# see https://flask-login.readthedocs.io/en/latest for details
login_manager = LoginManager()
login_manager.init_app(app)

# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


# Flask-login helper to retrieve user from DB
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# Thread for listening to UDP messages from mobile app
# udp_thread = Thread(target=listen_udp_msg, args=(app.app_context(),))
# udp_thread.start()

# Thread for listening to TCP messages from mobile app
tcp_thread = Thread(target=listen_tcp_msg, args=(app.app_context(),))
tcp_thread.start()

# Thread for listening to TCP messages from developers
tcp_dev_thread = Thread(target=tcp_reverse_flow, args=(app.app_context(),))
tcp_dev_thread.start()

# Global variable with permissions options
# Get permissions list
permissions_file = os.path.join('openivn', 'utilities',
                                'permissions_options.json')
with open(permissions_file, 'r') as infile:
    PERMISSIONS_GROUPS = json.load(infile)

# Application logging
#
# Levels: (explanations for when to use each level, in increasing severity)
# CRITICAL: program can't continue executing, very bad
# WARNING: indication of something unexpected
# ERROR: more serious problem, something couldn't be accomplished
# INFO: report events that occur during normal operation of program
# DEBUG: very detailed output for fault investigation
#
# Events at INFO level and above will be logged
logging.basicConfig(filename='log.log', level=logging.INFO)

# Create/clear a file to be used for testing UDP streaming
UDP_TEST_FILE = os.path.join(os.getcwd(), 'var', 'udp_test_file.txt')

# Create/clear a file to be used for testing TCP streaming
TCP_TEST_FILE = os.path.join(os.getcwd(), 'var', 'tcp_test_file.txt')

# Dictionary storing DBC information
# Key = vehicle str, value = DBC dictionary
GLOBAL_DBC = {}
