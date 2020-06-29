"""
OpenIVN index view.

URLs:
/
"""
import flask
import openivn
import logging
from flask_login import current_user


@openivn.app.route('/', methods=["GET"])
def show_index():
    """Display / route."""
    # Context to render template
    # logging.info("/views/index.py:show_index ran")

    context = {
        "permissions": openivn.PERMISSIONS_GROUPS
    }

    # Show user Developer Dashboard if logged in
    if current_user.is_authenticated:
        return flask.render_template("dashboard.html", **context)

    return flask.render_template("index.html", **context)
