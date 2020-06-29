"""API route to delete a DBC."""
from collections import defaultdict
import flask
import os
import openivn
import shutil
from openivn.utilities.decorators import authenticate_request, time_it
from openivn.model import get_db


@openivn.app.route('/api/v1/delDBC/', methods=["GET"])
@authenticate_request
@time_it
def del_dbc():
    """
    :param:     make (str)
                model (str)
                year (str)
    :return:    Deleted: DBC found and deleted
    """
    year = flask.request.args['year']
    car_make = flask.request.args['make']
    model = flask.request.args['model']

    run_name = car_make + '_' + model + '_' + year

    cursor = get_db().cursor()

    sql_cmd = "DELETE FROM vehicles WHERE vehicle_id = ?"
    cursor.execute(sql_cmd, (run_name,))
    get_db().commit()
    print(os.getcwd())

    try:
        shutil.rmtree(os.path.join(os.getcwd(), 'DBCs', run_name))
        os.remove(os.path.join(os.getcwd(), 'Downloads', run_name + '.zip'))
    except OSError:
        pass

    response = {
        "status": "Deleted",
        "url": flask.request.path
    }

    return flask.jsonify(**response)
