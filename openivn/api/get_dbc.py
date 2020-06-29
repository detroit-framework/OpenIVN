"""API route to search for the DBC. If found it is sent back if not a request for data is sent."""
from collections import defaultdict
import flask
import pathlib
import openivn
import logging
from openivn.utilities.decorators import authenticate_request, time_it
from openivn.model import get_db


@openivn.app.route('/api/v1/getDBC/', methods=["GET"])
@authenticate_request
@time_it
def get_dbc():
    """
    :param:     make (str)
                model (str)
                year (str)
    :return:    Found: json results for dbc file
                Processing: status of processing
                Not Found: Receiver should then request generateDBC to create
                dbc file and then poll this endpoint to check its status
    """
    year = flask.request.args['year']
    car_make = flask.request.args['make']
    model = flask.request.args['model']

    response = get_dbc_helper(car_make, model, year)

    return flask.jsonify(**response)


def get_run_name(car_make, model, year):
    run_name = car_make + '_' + model + '_' + year
    # This will strip leading and trailing whitespace
    return run_name.strip()


def get_results_paths(run_name):
    results_folder = pathlib.Path.cwd() / 'DBCs' / run_name
    results = results_folder / (run_name + '_dbc.txt')
    return results_folder, results


def get_dbc_status(car_make, model, year):
    run_name = get_run_name(car_make, model, year)

    cursor = get_db().cursor()
    sql_cmd = f'SELECT dbc FROM vehicles WHERE vehicle_id="{run_name}"'
    dbc_flag = cursor.execute(sql_cmd).fetchone()

    if dbc_flag:
        dbc_flag = dbc_flag['dbc']

    if dbc_flag:
        if dbc_flag == 1:  # 1 found
            results_folder, results = get_results_paths(run_name)
            if results_folder.exists() and results.exists():
                return "Found"
            else:
                return "Not Found"
        else:  # 2 processing
            return "Processing"
    else:  # 0 not found
        return "Not Found"


def is_dbc_available(car_make, model, year):
    if "Found" == get_dbc_status(car_make, model, year):
        return True
    else:
        return False


def get_dbc_helper(car_make, model, year, path=True):
    run_name = get_run_name(car_make, model, year)
    results_folder, results = get_results_paths(run_name)
    status = get_dbc_status(car_make, model, year)

    data = {}
    if status == 'Found':
        with open(results, 'r') as f:
            for line in f:
                item = eval(line)
                data[item['column']] = item

    if path:
        response = {
            "status": status,
            "data": data,
            "url": flask.request.path
        }
    else:
        response = {
            "status": status,
            "data": data,
        }

    return response
