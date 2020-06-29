import openivn
from flask import jsonify


class UsefulError(Exception):
    """A class to provide application clients with useful error messages."""
    def __init__(self, message, status_code=None, payload=None):
        # Create Exception because this is an inherited class
        Exception.__init__(self)
        self.message = message
        if status_code:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


# Register an error handler for this class
# so that it might be used in view or api functions
@openivn.app.errorhandler(UsefulError)
def handle_useful_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
