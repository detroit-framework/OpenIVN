"""API route to look up make model year wheelbase from the VIN."""
import flask
import openivn
from openivn.utilities.vin_lookup import vin_lookup
from openivn.utilities.get_specs import get_specs
from openivn.utilities.decorators import authenticate_request, time_it
from openivn.api.get_dbc import is_dbc_available


@openivn.app.route('/api/v1/vin/<string:vin>', methods=["GET"])
@authenticate_request
@time_it
def get_vin(vin):
    """Return vehicle information based on VIN."""
    # Response object
    response = {
        'url': flask.request.path,
    }

    # Get information using the VIN
    try:
        data = vin_lookup(vin)
    except Exception as e:
        response = {
            "error_message": e.args[0]
        }
        return flask.jsonify(**response), 500

    response['make'] = data['make']
    response['model'] = data['model']
    response['year'] = data['model_year']

    # If trim is available, use it to get exact wheelbase information
    # Otherwise, get the generic wheelbase
    trim = flask.request.args.get('trim', default=None, type=str)

    # Get vehicle specs
    try:
        specs = get_specs(data['make'], data['model'], data['model_year'],
                          trim)
    except Exception as e:
        response = {
            "error_message": e.args[0]
        }
        return flask.jsonify(**response), 500

    # response['wheelbase'] = specs['wheelbase']

    # Add trim or list of available trim_options to response,
    # based on whether a trim was provided with the request
    if trim:
        response['trim'] = specs['trim']
    else:
        response['trim_options'] = specs['trim_options']

    # include status of DBC
    response['dbc_available'] = is_dbc_available(response['make'], response['model'], response['year'])

    return flask.jsonify(**response)
