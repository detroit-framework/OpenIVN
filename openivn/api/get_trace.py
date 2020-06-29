"""API route to get traces."""
import flask
import openivn
from openivn.utilities.decorators import authenticate_request, time_it
from openivn.model import get_db


@openivn.app.route('/api/v1/get_trace/', methods=["GET"])
@authenticate_request
@time_it
def get_trace():
    """
    :requires:

    :param:     Body params:
                    trace_id (int)

                    NOTE: all of the following must be provided to search for
                    make (str)
                    model (str)
                    year (str)

                    user_id (str)

                    app_id (int)

                    translation (int) 0 backend 1 frontend
    :return:
                "traces matching specified parameters"
    """

    request = eval(flask.request.form['request'])

    response = {"url": flask.request.path}

    keys = ['trace_id', 'vehicle_id', 'user_id', 'app_id', 'translation']
    where_cmd = ''
    first = True
    for k in keys:
        if k in request:
            if first:
                where_cmd += ' WHERE'
                first = False
            else:
                where_cmd += ' AND'
            where_cmd += f' {k}= {request[k]}'

    sql_cmd = 'SELECT trace_id FROM traces ' + where_cmd

    cursor = get_db().cursor()
    cursor.execute(sql_cmd)
    response['results'] = cursor.fetchall()

    return flask.jsonify(**response)


