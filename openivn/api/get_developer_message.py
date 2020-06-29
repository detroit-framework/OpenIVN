"""API route to get developer messages."""
import flask
import openivn
from openivn.model import get_db
from openivn.utilities.decorators import authenticate_request
from openivn.utilities.useful_error import UsefulError


@openivn.app.route('/api/v1/messages/<int:app_id>', methods=["GET"])
@authenticate_request
def get_developer_message(app_id):
    """Return message from developer for app_id."""
    # Set up access to database
    db = get_db()

    # Get message for the app
    sql_command = "SELECT * FROM developer_messages WHERE app_id = ?"
    dev_message = db.execute(sql_command, (app_id,)).fetchone()

    # Return error message if app was not found in database
    if not dev_message:
        raise UsefulError('App not found', status_code=404)

    # Create response object
    response = {
        'url': flask.request.path,
        'app_id': app_id,
        'message': dev_message['message'],
        'timestamp': dev_message['timestamp']
    }

    return flask.jsonify(**response)
