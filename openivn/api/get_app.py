"""API route for getting detailed information on a specific app."""
import flask
import openivn
from openivn.utilities.decorators import authenticate_request, time_it
from openivn.utilities.useful_error import UsefulError
from openivn.model import get_db


@openivn.app.route('/api/v1/apps/<int:app_id_slug>/', methods=["GET"])
@authenticate_request
@time_it
def get_app(app_id_slug):
    """Returns information on a specific app."""
    # Set up cursor to access database
    cursor = get_db().cursor()

    # Get general information on the app
    app_info = cursor.execute("SELECT * FROM apps WHERE app_id = ?",
                              (app_id_slug,)).fetchone()

    # Raise error if app was not found in database
    if not app_info:
        raise UsefulError('App not found', status_code=404)

    author_name = cursor.execute("SELECT * FROM users WHERE id = ?",
                                 (app_info["author_id"],)).fetchone()["name"]

    # Get permission groups information
    perm_groups = cursor.execute("SELECT * FROM permissions WHERE app_id = ?",
                                 (app_id_slug,)).fetchone()

    # Dictionary to store permissions for the response
    # Key = permission group, value = True/False
    perms_dict = {}

    # Format permission group names for response
    for perm in perm_groups:
        if perm != "app_id":
            # Remove underscores in name and
            # replace integer with a boolean value
            if perm_groups[perm]:
                perms_dict[perm.replace("_", " ")] = True
            else:
                perms_dict[perm.replace("_", " ")] = False

    # Assemble response
    response = {
        'url': flask.request.path,
        'id': app_info['app_id'],
        'name': app_info['name'],
        'author_id': app_info['author_id'],
        'author_name': author_name,
        'description': app_info['description'],
        'permissions': perms_dict,
        'streaming': app_info['streaming']
    }

    return flask.jsonify(**response)
