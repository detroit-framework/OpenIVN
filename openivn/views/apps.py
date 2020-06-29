"""
OpenIVN apps view.

URLs:
/apps/
"""
import flask
import openivn
import logging
from openivn.model import get_db
from flask_login import login_required, current_user


@openivn.app.route('/apps/', methods=["GET"])
@login_required
def view_apps():
    """Display a user's apps and related info."""
    # logging.info("/views/apps.py:view_apps ran")
    context = {
        'apps': []
    }

    # Set up access to database
    db = get_db()

    # Retrieve list of user's apps from database
    context['apps'] = db.execute(
        "SELECT * FROM apps WHERE author_id = ?",
        (current_user.id,)
    ).fetchall()

    # Retrieve permissions for each app
    for a in context['apps']:
        perm_cols = db.execute(
            "SELECT * FROM permissions WHERE app_id = ?", (a['app_id'],)
        ).fetchone()

        # Will store permissions that have been selected
        a['permissions'] = []

        for p in perm_cols:
            # Skip the column app_id because it's not a permission
            # Skip permissions which were not selected
            if p == "app_id" or perm_cols[p] == 0:
                continue
            a['permissions'].append(p)

        # Sort permissions alphabetically so they look nicer
        a['permissions'].sort()

    return flask.render_template("apps.html", **context)
