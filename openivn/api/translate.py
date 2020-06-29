"""API route to translate raw file with a dbc."""
import flask
import zipfile
import shutil
import os
import json
from time import time
from _sqlite3 import IntegrityError
import openivn
from openivn.utilities.decorators import authenticate_request, time_it
from openivn.api.get_dbc import get_dbc_helper
from openivn.model import get_db
import bitarray
import logging
fine_grained_timing = True


@openivn.app.route('/api/v1/translate/', methods=["POST"])
@authenticate_request
@time_it
def translate_dbc():
    """
    :requires:
                DBC exists for make/model/year
    :param:     URL params:
                    make (str)
                    model (str)
                    year (str)
                    user_id (str)
                    app_id
                Body Params
                    zip_file - contains 1 file

    :return:
                "No DBC" if DBC is not found
                "Translated"
    """
    year = flask.request.args['year']
    car_make = flask.request.args['make']
    model = flask.request.args['model']
    username = flask.request.args['user_id']
    app_id = flask.request.args['app_id']
    file = flask.request.files['zip_file']

    permission_items = permissions_helper(app_id)
    # logging.info(f"Permission Items: {permission_items}")

    response_dbc = get_dbc_helper(car_make, model, year)
    run_name = car_make + '_' + model + '_' + year

    response = {"url": flask.request.path}

    if response_dbc["status"] != "Found":
        response["status"] = "No DBC"
    else:
        response["status"] = "Translated and saved"
        translated = {}
        folder = os.path.join(os.getcwd(), 'Downloads',
                              file.filename.replace('.zip', ''))
        zip_file = os.path.join(os.getcwd(),
                                'Downloads', file.filename)
        if fine_grained_timing:
            ts = time()
        file.save(zip_file)
        unzip(zip_file, folder)
        if fine_grained_timing:
            unzip_save_time = time() - ts

        # sub_dir = os.path.join(folder, file.filename.replace('.zip', ''))
        sub_dir = folder
        filename = [f for f in os.listdir(sub_dir) if os.path.isfile(os.path.join(sub_dir, f))][0]
        time_value = {}

        for i in permission_items:
            translated[i] = {}
            try:
                translated[i]["dbc"] = response_dbc["data"][i]
            except KeyError as key_error:
                logging.critical(f"{key_error} for i = {i}")
                continue
            time_value[i] = []
        if fine_grained_timing:
            ts = time()
        with open(os.path.join(sub_dir, filename), 'r') as f:
            linez = f.readlines()
            for line in linez:
                line = line.strip()
                data = line.split(',')
                timestmp = float(data[0])
                can_id = int(data[1])
                dbc = int(data[2])
                can_data = data[3]
                for val in translated.keys():
                    if 'dbc' not in translated[val]:
                        continue
                    if translated[val]["dbc"]["DBC"] == dbc and \
                       translated[val]["dbc"]["ID"] == can_id:
                        time_value[val].append(
                            [timestmp, translate(can_data,
                                                 translated[val]["dbc"]["Start"],
                                                 translated[val]["dbc"]["End"],
                                                 translated[val]["dbc"]["Coefficient"],
                                                 translated[val]["dbc"]["Intercept"])])

        for key, val in time_value.items():
            if not val:
                del translated[key]["dbc"]
                translated[key]["series"] = "Not In Trace"
                continue

            first_t, _ = val[0]
            last_t, _ = val[-1]
            res = [v for _, v in val]
            freq = len(val)/(last_t-first_t)
            translated[key]["sampling_freq"] = freq
            translated[key]["series"] = res
            translated[key]["base_timestamp"] = first_t
            del translated[key]["dbc"]

        if fine_grained_timing:
            translating_time = time() - ts

        cursor = get_db().cursor()

        # save backend file
        sql_cmd = 'INSERT INTO traces(vehicle_id, user_id, app_id) VALUES(?, ?, ?)'
        try:
            cursor.execute(sql_cmd, (run_name, username, app_id))
        except IntegrityError:
            response["status"] = 'Invalid username or app_id'
            return flask.jsonify(**response)
        back_end_key = cursor.lastrowid
        with open(os.path.join(os.getcwd(), 'Traces', str(back_end_key) + '.json'), 'w+') as outfile:
            json.dump(translated, outfile, indent=4)

        shutil.rmtree(folder)

    if fine_grained_timing:
        # response['Statistics'] = f'save and extract: {unzip_save_time}. translating time {translating_time}'
        logging.info(f'Fine Grained Timing for Translate -> '
                     f'save and extract: {unzip_save_time}. translating time {translating_time}.')
    get_db().commit()
    return flask.jsonify(**response)


def permissions_helper(app_id):
    permissions = get_db().execute(
        "SELECT * FROM permissions WHERE app_id = ?", (app_id,)
    ).fetchone()
    permission_items = []
    # iterate through all the permissions returned
    # the first item is the app_id so we ignore it
    for i, v in permissions.items():
        if i == 'app_id':
            continue
        if v:
            permission_items.extend(list(openivn.PERMISSIONS_GROUPS[i]))

    return permission_items


def dbc_helper(run_name):
    dbc = get_dbc_helper(*run_name.split('_'), False)
    # logging.info(f"dbc loaded status {dbc['status']}")
    return dbc["data"]


def translate(data, start, end, scale, offset):
    bits = bitarray.bitarray(bin(int(data, 16))[2:].zfill(64))
    if scale == 0:
        return float(int(bits[start:end+1].to01(), 2))
    else:
        return (float(int(bits[start:end+1].to01(), 2)) * float(scale) +
                float(offset))


def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        zf.extractall(dest_dir)