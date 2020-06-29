"""
OpenIVN UDP test view.

URLs:
/udp/test/
/udp/delete/
"""
import flask
import openivn
import logging
from flask_login import login_required
import time


@openivn.app.route('/udp/test/', methods=["GET"])
@login_required
def test_udp():
    """Display UDP testing route."""
    # Context for template
    context = {
        "data": []
    }

    with open(openivn.UDP_TEST_FILE, 'r') as infile:
        for line in infile:
            context['data'].append(line)

    context['current_time'] = time.asctime()

    return flask.render_template("udp_test.html", **context)


@openivn.app.route('/udp/delete/', methods=["GET"])
@login_required
def clear_udp():
    """Clear UDP testing file."""
    with open(openivn.UDP_TEST_FILE, 'w'):
        logging.info(f"UDP testing file cleared -- {time.asctime()}")

    return flask.redirect(flask.url_for('test_udp'))
