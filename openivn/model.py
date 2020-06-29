"""OpenIVN model (database) API."""
import sqlite3
import flask
import openivn


def dict_factory(cursor, row):
    """Summary line."""
    output = {}
    for idx, col in enumerate(cursor.description):
        output[col[0]] = row[idx]
    return output


def get_db():
    """Open a new database connection."""
    if not hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db = sqlite3.connect(
            openivn.app.config['DATABASE_FILENAME'])
        flask.g.sqlite_db.row_factory = dict_factory

        # Foreign keys have to be enabled per-connection.  This is an sqlite3
        # backwards compatibility thing.
        flask.g.sqlite_db.execute("PRAGMA foreign_keys = ON")

    return flask.g.sqlite_db


# Commented out to avoid errors while implementing OAuth
# @openivn.app.teardown_appcontext
# def close_db(error):
#     """Close the database at the end of a request."""
#     # Assertion needed to avoid style error
#     assert error or not error
#     if hasattr(flask.g, 'sqlite_db'):
#         flask.g.sqlite_db.commit()
#         flask.g.sqlite_db.close()
