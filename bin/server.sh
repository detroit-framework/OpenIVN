#!/bin/bash
# OpenIVN Server Script

# Stop on errors
set -Eeuo pipefail

# Sanity check command line options
usage() {
    echo "Usage: $0 (start-dev|start-prod|stop-dev|stop-prod|restart-dev|restart-prod)"
    echo -e "\t-dev options manage a localhost server"
    echo -e "\t-prod options manage a production-grade proxy server setup open to the Internet"
}

if [ $# -ne 1 ]; then
    usage
    exit 1
fi

start-dev() {
    # Set environment variables
    # Set FLASK_DEBUG to False to allow threads to run
    export FLASK_DEBUG=False
    export FLASK_APP=openivn
    export OPENIVN_SETTINGS=config.py

    # Run development server with adhoc SSL cert/key
    flask run --cert adhoc --host 127.0.0.1 --port 1609 --with-threads #&> /dev/null &
}

start-prod() {
    # Set environment variables
    export FLASK_DEBUG=False
    export FLASK_APP=openivn
    export OPENIVN_SETTINGS=config.py

    # Run Nginx (reverse-proxy server)
    # Note that Nginx should be configured to listen on port 1609
    # Nginx will receive HTTPS requests and reverse-proxy them to Gunicorn
    sudo systemctl start nginx

    # Run Gunicorn (WSGI HTTP server)
    # Gunicorn will receive unencrypted HTTP requests from Nginx
    # Gunicorn log output is formatted as:
    # GUNICORN: IP_Address - - [Date:Time Timezone_Offset] Request_Method Route Protocol Status User_Agent
    # Note that %(r)s logs the status line (GET / HTTP/1.0). The middle "/" is the route accessed in that request.
    gunicorn openivn:app \
        --workers=65 \
        --bind 127.0.0.1:1610 \
        --daemon \
        --access-logfile log.log \
        --access-logformat "GUNICORN: %({x-real-ip}i)s - - %(t)s %(r)s %(s)s %(a)s"
}

start-prod-output() {
    # Set environment variables
    export FLASK_DEBUG=False
    export FLASK_APP=openivn
    export OPENIVN_SETTINGS=config.py

    # Run Nginx (reverse-proxy server)
    # Note that Nginx should be configured to listen on port 1609
    # Nginx will receive HTTPS requests and reverse-proxy them to Gunicorn
    sudo systemctl start nginx

    # Run Gunicorn (WSGI HTTP server)
    # Gunicorn will receive unencrypted HTTP requests from Nginx
    gunicorn --workers=65 --bind 127.0.0.1:1610 openivn:app > stdout.txt
}

stop-dev() {
    # Kill Flask dev server
    pkill -f 'flask run --cert adhoc --host 127.0.0.1 --port 1609'
}

stop-prod() {

    # Kill Nginx
    sudo systemctl stop nginx

    # Kill Gunicorn
    pkill -f gunicorn
}

case $1 in
  "start-dev")
    start-dev
    ;;

  "start-prod")
    start-prod
    ;;

  "stop-dev")
    stop-dev
    ;;

  "stop-prod")
    stop-prod
    ;;

  "restart-dev")
    stop-dev
    start-dev
    ;;

  "restart-prod")
    stop-prod
    start-prod
    ;;

  "start-prod-output")
    start-prod-output
    ;;

  *)
    usage
    exit 1
    ;;
esac
