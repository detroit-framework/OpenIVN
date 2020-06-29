"""API route called after get_dbc.py requests data. App should send a zipped file of all the files."""
import csv
import json
from datetime import datetime
import pathlib
import shutil
import zipfile
import flask
import multiprocessing as mp

import openivn
from openivn.api.get_dbc import get_dbc_status
from openivn.utilities.decorators import authenticate_request, time_it
from openivn.model import get_db

from ReverseEngineerLibrary import reverse_engineer_dbc


@openivn.app.route('/api/v1/generateDBC/', methods=["POST"])
@authenticate_request
@time_it
def generate_dbc():
    """
    :param:     make (str)
                model (str)
                year (str)
                wheelbase (str)
                zip_file (zipfile): contains all necessary file to reverse engineer the DBC
                force_run (optional): set to 'True' if you want to rerun pipeline regardless of existing DBC
    :return:
                Run status: if the run was started
    """
    car_make = flask.request.args['make']
    model = flask.request.args['model']
    year = flask.request.args['year']
    wheelbase = flask.request.args['wheelbase']
    force_run = 'force_run' in flask.request.args and "True" == flask.request.args['force_run']
    run_name = car_make + '_' + model + '_' + year

    if not force_run:
        dbc_status = get_dbc_status(car_make, model, year)
        if "Found" == dbc_status:
            return flask.jsonify({"run_status": "Completed", "url": flask.request.path})
        elif "Processing" == dbc_status:
            return flask.jsonify({"run_status": "Processing", "url": flask.request.path})

    # download our trace files
    file = flask.request.files['zip_file']
    zip_file = pathlib.Path.cwd() / 'Downloads' / \
               (run_name + '_' + datetime.now().strftime("%Y_%m_%d_%H:%M:%S:%f") + '.zip')
    file.save(zip_file)

    # remove if it already exists
    run_folder = pathlib.Path.cwd() / 'DBCs' / run_name
    if run_folder.exists() and run_folder.is_dir():
        shutil.rmtree(run_folder)
    # make our run folder and parents if needed
    run_folder.mkdir(parents=True, exist_ok=True)

    # extract the trace data into the run folder
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(run_folder)

    # convert txt files to json files
    convert_txt_to_json(run_folder / 'Phase1.txt', run_folder / 'Phase1.json')
    events_folder = run_folder / 'Events'
    events_folder.mkdir(exist_ok=True, parents=True)
    for file in run_folder.iterdir():
        # assumes that all txt files that are not Phase1 are the event files, so they have a comma in the name
        if file.suffix == '.txt' and not 'Phase1' == file.stem:
            new_name = file.stem.split(',')[1].strip() + '.json'
            convert_txt_to_json(file, events_folder / new_name)

    # Update the vehicle dbc status in our database to be processing
    db_conn = get_db()
    cursor = db_conn.cursor()
    sql_cmd = "INSERT OR REPLACE INTO vehicles(vehicle_id, make, model, year, dbc) VALUES (?, ?, ?, ?, 2);"
    cursor.execute(sql_cmd, (run_name, car_make, model, int(year)))
    db_conn.commit()

    # Start this as a process and set daemon to False
    reverse_engineer_parameters = {'folder_path': run_folder}
    proc = mp.Process(target=reverse_engineer_dbc, args=(reverse_engineer_parameters))
    proc.daemon = False
    proc.start()

    return flask.jsonify({"run_status": "Processing", "url": flask.request.path})


def convert_txt_to_json(txt_file_path, json_file_path):
    # bus: read as int
    # id: read as int
    # data: read as string, convert to uppercase
    # timestamp read as float
    # timestamp,id,bus,data
    # 1593294889.204,144,1,05003e0064390000 --> {"bus":1,"id":144,"data":"05003E0064390000","timestamp":1593294889.204}
    with open(txt_file_path, 'r') as txt_file, open(json_file_path, 'w') as json_file:
        txt_file_as_csv = csv.DictReader(txt_file, fieldnames=['timestamp', 'id', 'bus', 'data'])
        for row in txt_file_as_csv:
            # skip malformed rows:
            if 'timestamp' not in row or 'id' not in row or 'bus' not in row or 'data' not in row:
                continue
            if None is row['timestamp'] or None is row['id'] or None is row['bus'] or None is row['data']:
                continue
            if 0 == len(row['timestamp']) or 0 == len(row['id']) or 0 == len(row['bus']) or 0 == len(row['data']):
                continue
            if not 16 == len(row['data']):
                continue
            row['timestamp'] = float(row['timestamp'])
            row['id'] = int(row['id'])
            row['bus'] = int(row['bus'])
            row['data'] = str(row['data']).upper()
            json.dump(row, json_file)
            print(file=json_file)  # append a newline
