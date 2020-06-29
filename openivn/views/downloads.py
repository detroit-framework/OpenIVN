"""
View & download the traces for a particular app.

URLs:
/downloads/
/traces/
"""
import os
import flask
import openivn
from openivn.model import get_db
from openivn.generate_alt_formats.generate_matlab import generate_matlab
from openivn.generate_alt_formats.generate_npy import generate_npy
from flask_login import login_required


# View for Downloads page
# List all traces available to download for a particular app
# Group these traces by date
# When a trace is clicked, it is downloaded

# Download function
# use flask.send_from_directory(directory, filename, as_attachment=True)

@openivn.app.route('/downloads/<int:app_id>/', methods=["GET"])
@login_required
def view_downloads(app_id):
    """Display translated traces for an app that are available to download."""
    # Set up access to database
    db = get_db()

    # Get app name from DB
    app_data = db.execute(
        "SELECT * FROM apps WHERE app_id = ?", (app_id,)
    ).fetchone()

    # Retrieve list of traces for this app
    traces = db.execute(
        "SELECT * FROM traces WHERE app_id = ?", (app_id,)
    ).fetchall()

    # Dictionary of trace files associated with each vehicle
    # Key = vehicle_id, value = list of tuples (timestamp, trace id)
    files = {}

    for trace in traces:
        # Vehicle ID already seen, just append to list
        try:
            files[trace['vehicle_id']].append(
                (trace['Timestamp'], trace['trace_id'])
            )
        # Never see vehicle ID before, initialize list
        except KeyError:
            files[trace['vehicle_id']] = [
                (trace['Timestamp'], trace['trace_id'])
            ]

    # Store data in context variable for access in HTML template
    context = {
        'app_name': app_data['name'],
        'files': files
    }

    return flask.render_template("downloads.html", **context)


@openivn.app.route('/traces/<int:trace_id>/', methods=["GET"])
@login_required
def download_trace(trace_id):
    """Download a trace."""
    # Determine file format requested by user
    file_format = flask.request.args.get('format')
    file_path = os.path.join("Traces", f"{trace_id}.json")

    if file_format == 'mat':
        # Translate JSON file to MATLAB container format
        generate_matlab(file_path)
        file_path = os.path.join("..", "Traces", f"{trace_id}.mat")
    elif file_format == 'npy':
        # Translate JSON file to NumPy container format
        generate_npy(file_path)
        file_path = os.path.join("..", "Traces", f"{trace_id}.npy")
    else:
        # Defaults to downloading JSON file
        file_path = os.path.join('..', file_path)

    return flask.send_file(file_path, mimetype='text/json', as_attachment=True)
