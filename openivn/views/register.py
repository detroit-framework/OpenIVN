"""
OpenIVN register view.

URLs:
/register/
"""
import flask
import openivn
import logging
from openivn.model import get_db
from flask_login import login_required, current_user


@openivn.app.route('/register/', methods=["GET", "POST"])
@login_required
def register():
    """Display registration route."""
    # logging.info("/views/register.py:register ran")
    context = {
        "permissions": openivn.PERMISSIONS_GROUPS.keys(),
    }

    if flask.request.method == "POST":
        # Set up access to database
        db = get_db()

        # Get data from POST request
        data = {
            'name': flask.request.form.get("app_name"),
            'author_id': current_user.id,
            'description': flask.request.form.get("description"),
            'permissions': {},
        }

        # Identify which permissions were selected by the user
        for group, g_dict in openivn.PERMISSIONS_GROUPS.items():
            if flask.request.form.get(group):
                for perm in g_dict.keys():
                    data['permissions'][perm] = True
            else:
                for perm in g_dict.keys():
                    data['permissions'][perm] = False

        # Determine if vehicular data will be made available for download
        # or if it will be streamed to an endpoint
        streaming = 0
        stream_endpoint = None
        if flask.request.form.get("data-radios") == "stream_data":
            streaming = 1
            stream_endpoint = flask.request.form.get('stream_endpoint')
            # If no endpoint was provided, treat as if the app requires
            # its data to be available for download later
            if not stream_endpoint:
                streaming = 0

        # Save app data to database
        db.execute("INSERT INTO apps(name, author_id, description, streaming, stream_endpoint) VALUES(?, ?, ?, ?, ?)", (data['name'], data['author_id'], data['description'], streaming, stream_endpoint)).fetchone()

        # Get the app's ID from database
        tmp_app = db.execute("SELECT * FROM apps WHERE name = ? AND author_id = ?", (data['name'], data['author_id'])).fetchone()
        app_id = tmp_app['app_id']

        # Start assembling SQL command to save permissions data
        sql_cmd = "INSERT INTO permissions(app_id"

        # Add new permissions
        for p in context['permissions']:
            sql_cmd += ", {0}".format(p)

        # Finish assembling SQL command
        sql_cmd += ") VALUES(?"
        question_marks = ", ?" * len(context['permissions'])
        sql_cmd += question_marks
        sql_cmd += ")"

        # This is what a sample SQL command looks like
        # "INSERT INTO permissions(app_id, Doors, Trunk, Hood, "
        #  "Windows, HVAC, Horn, Lights, Windshield_Wipers, "
        #  "Turn_Signals, Parking_Brake, Mirrors, Seat_Belts)"
        #  "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

        # Now get the data from the POST request
        col_vals = [app_id]
        for p in context['permissions']:
            if flask.request.form.get(p):
                col_vals += [1]
            else:
                col_vals += [0]

        # execute function requires the values be formatted as a tuple
        # like this: (app_id, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
        tup = tuple(col_vals)

        # Save permissions data to database
        db.execute(sql_cmd, tup)
        db.commit()

        # Send user to apps page
        return flask.redirect(flask.url_for("view_apps"))

    # Remove the underscores in the names for pretty output
    # This is done at the end, before rendering the web page because the
    # original key names with underscores are necessary for things above.
    # context['permissions'] = [x.replace("_", " ") for x in
    #                           context['permissions']]

    # Allow GET request to fall here
    return flask.render_template("register.html", **context)
