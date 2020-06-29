"""
OpenIVN authentication endpoints.

URLS:
/login
/login/callback/
/logout/
"""

import flask
import openivn
import requests
import json
from flask_login import login_required, login_user, logout_user
from openivn.utilities.get_google_provider_config import get_google_provider_config
from openivn.utilities.user import User


@openivn.app.route('/login', methods=["GET", "POST"])
def login():
    """
    Handle login logic.

    See https://realpython.com/flask-google-login/ for more.
    """
    # Determine URL for Google login
    google_provider_cfg = get_google_provider_config()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Build request for Google login
    # oauthlib makes the actual request to Google
    # Declared what OAuth2 scopes we wanted
    request_uri = openivn.client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=flask.request.base_url + "/callback/",
        scope=["openid", "email", "profile"],
    )

    return flask.redirect(request_uri)


@openivn.app.route("/login/callback/")
def callback():
    """Handle Google login callback."""
    # Get authorization code sent by Google
    code = flask.request.args.get("code")

    # Determine URL to get tokens that allow us to ask for data for a user
    google_provider_cfg = get_google_provider_config()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prep and send request to get tokens
    token_url, headers, body = openivn.client.prepare_token_request(
        token_endpoint,
        authorization_response=flask.request.url,
        redirect_url=flask.request.base_url,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(openivn.GOOGLE_CLIENT_ID, openivn.GOOGLE_CLIENT_SECRET)
    )

    # Parse tokens
    openivn.client.parse_request_body_response(
        json.dumps(token_response.json())
    )

    # Determine Google URL that provides user's profile information
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]

    # Use oauthlib to add the token to the request
    uri, headers, body = openivn.client.add_token(userinfo_endpoint)

    # Send request to get user info
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # Check that user or Google has verified the email address
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        user_name = userinfo_response.json()["name"]
        user_email = userinfo_response.json()["email"]
    else:
        return "User email not verified by Google", 400

    # Add user to DB if not already in it
    user = User(id_in=unique_id, name_in=user_name, email_in=user_email)
    if not User.get(unique_id):
        User.add(unique_id, user_name, user_email)

    # Log in user
    login_user(user)

    # Send user back to homepage
    return flask.redirect(flask.url_for("show_index"))


@openivn.app.route("/logout/")
@login_required
def logout():
    logout_user()
    return flask.redirect(flask.url_for("show_index"))
