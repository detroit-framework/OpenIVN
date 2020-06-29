"""
OpenIVN edit app view.

URLs:
/edit/
"""
import flask
import openivn
import logging
from openivn.model import get_db
from flask_login import login_required, current_user


@openivn.app.route('/edit/<int:app_id>', methods=["GET", "POST"])
@login_required
def edit_app(app_id):
    """Display edit app route."""
    # Set up access to database
    db = get_db()

    # Render web page
    if flask.request.method == "GET":
        # Get app info
        app_info = db.execute(
            "SELECT * FROM apps WHERE app_id = ?", (app_id,)
        ).fetchone()

        # Add relevant info to the context
        context = {
            'app_name': app_info['name'],
            'app_description': app_info['description']
        }

        # Add relevant data for streaming
        if app_info['streaming']:
            context['streaming'] = True
            context['stream_endpoint'] = app_info['stream_endpoint']
        else:
            context['streaming'] = False

        # Get permissions info
        permissions_cols = db.execute(
            "SELECT * FROM permissions WHERE app_id = ?", (app_id,)
        ).fetchone()

        # Add permissions data to context
        # Permissions are formatted as a list of tuples
        # (permission name, 0|1) where 0 = not selected, 1 = selected
        context['permissions'] = []

        # Format permissions names and add to the context
        for p in permissions_cols:
            # Skip adding the app_id column
            if p != "app_id":
                tup = (p, permissions_cols[p])
                context['permissions'].append(tup)

        # Sort permissions alphabetically so it looks nice
        context['permissions'].sort(key=lambda x: x[0])

        return flask.render_template("edit_app.html", **context)

    # Handle edits to app
    elif flask.request.method == "POST":
        # Get data from POST request
        app_name = flask.request.form.get("app_name")
        app_description = flask.request.form.get("description")
        app_permissions = {}

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

        # Update app data in database
        db.execute(
            "UPDATE apps SET name = ?, description = ?, streaming = ?, stream_endpoint = ? WHERE app_id = ?",
            (app_name, app_description, streaming, stream_endpoint, app_id,)
        )

        # Start constructing SQL statement to update permissions in DB
        update_perms_sql_stmt = "UPDATE permissions SET "

        # Iterate over the permission groups
        for group in openivn.PERMISSIONS_GROUPS.keys():
            # Mark the permission as True (1) if selected by user
            # Note that the space after the integer is intentional
            if flask.request.form.get(group):
                update_perms_sql_stmt += f"{group} = 1, "
            else:
                update_perms_sql_stmt += f"{group} = 0, "

        # Remove trailing space and comma from last parameter
        update_perms_sql_stmt = update_perms_sql_stmt[:-2]

        # Need to include app id to identify the correct row to update
        # Pass parameter using "?" to prevent against any funny business,
        # such as SQL injection
        update_perms_sql_stmt += " WHERE app_id = ?"

        # Update permissions in DB
        db.execute(update_perms_sql_stmt, (app_id,))
        db.commit()  # save changes to DB

        # Send user to apps page
        return flask.redirect(flask.url_for("view_apps"))

    # This should never happen since this route only accepts GET or POST
    # requests, but it's good to have a message just in case...
    else:
        return "This should never happen. Error in edit_app.py."
