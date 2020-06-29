"""OpenIVN Decorators."""
import functools
import flask
import os
import time
import logging


def time_it(method):
    @functools.wraps(method)
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        logging.info(f'TIMING: {method.__name__} ran for {get_time(te-ts)}')
        return result
    return timed


def get_time(ts):
    """Used for Timing."""
    ts = ts % (24 * 3600)
    ts %= 3600
    minutes = ts // 60
    ts %= 60
    seconds = ts
    ts %= 1
    milli = int(ts * 1000)
    return "%d minutes %d seconds %d milliseconds" % (minutes, seconds, milli)




def authenticate_request(func):
    """Verifies that request is made from an authorized source."""
    # Preserve information about original function (like __name__, __doc__)
    @functools.wraps(func)
    # Define wrapper function, passing through all positional and keyword
    # arguments included in func
    def wrapper(*args, **kwargs):
        # Do something before the wrapped function runs
        # In this case, authenticate the requesting party

        # Extract the user's API key from the request
        user_key = flask.request.headers.get("x-api-key")

        # Read in set of valid API keys from file
        key_file = os.path.join(os.getcwd(), 'openivn', 'api.key')
        api_keys = set()
        with open(key_file, 'r') as f:
            for key in f.readlines():
                api_keys.add(key.strip())

        # Allow access to function only if user is authorized
        if user_key and user_key in api_keys:
            # We could also just call func(*args, **kwargs) without returning
            # the function. We return the func so that the wrapper function
            # returns the return value of the decorated function (i.e. return
            # the return value of func)
            return func(*args, **kwargs)
        else:
            flask.abort(401)  # Unauthorized
    return wrapper
