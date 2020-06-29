"""API route for getting list of apps."""
import flask
import openivn
from openivn.utilities.decorators import authenticate_request, time_it
from openivn.model import get_db


@openivn.app.route('/api/v1/apps/', methods=["GET"])
@authenticate_request
@time_it
def get_app_list():
    """Returns apps registered with OpenIVN."""
    # Base response
    response = {
        'url': flask.request.path,
        'apps': []
    }

    # Set up cursor to access database
    cursor = get_db().cursor()

    # Get list of all apps
    apps_list = cursor.execute("SELECT * FROM apps").fetchall()

    # Assemble app dictionary and append to list in response object
    for app in apps_list:
        author_name = cursor.execute("SELECT * FROM users WHERE id = ?",
                                     (app["author_id"],)).fetchone()["name"]
        tmp_app = {
            'id': app['app_id'],
            'name': app['name'],
            'author_id': app['author_id'],
            'author_name': author_name,
            'description': app['description'],
            'streaming': app['streaming'],
            'url': '/api/v1/apps/{0}/'.format(app['app_id'])
        }
        response['apps'].append(tmp_app)

    return flask.jsonify(**response)
