"""
OpenIVN TCP test view.

URLs:
/tcp/test/
/tcp/delete/
"""
import flask
import openivn
import logging
from flask_login import login_required
import time


@openivn.app.route('/tcp/test/', methods=["GET"])
@login_required
def test_tcp():
    """Display TCP testing route."""
    # Context for template
    context = {
        "data": []
    }

    with open(openivn.TCP_TEST_FILE, 'r') as infile:
        for line in infile:
            context['data'].append(line)

    context['current_time'] = time.asctime()

    return flask.render_template("tcp_test.html", **context)


@openivn.app.route('/tcp/delete/', methods=["GET"])
@login_required
def clear_tcp():
    """Clear TCP testing file."""
    with open(openivn.TCP_TEST_FILE, 'w'):
        logging.info(f"TCP testing file cleared -- {time.asctime()}")

    return flask.redirect(flask.url_for('test_tcp'))
