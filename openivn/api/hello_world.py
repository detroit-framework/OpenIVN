"""REST API for a test message."""
import flask
import openivn
from openivn.utilities.decorators import authenticate_request, time_it


@openivn.app.route('/api/v1/hello_world/', methods=["GET"])
@time_it
def get_hello_world():
    """Returns a hello world message."""

    context = {
        "message_text": "Hello world!",
        "url": flask.request.path,
    }
    return flask.jsonify(**context)
