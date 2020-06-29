#!/bin/bash
# OpenIVN Database Script

# Stop on errors
set -Eeuo pipefail

# Sanity check command line options
usage() {
    echo "Usage: $0 (setup-dev|setup-prod|destroy|reset-dev|reset-prod|dump)"
    echo -e "\t-dev options add testing data to tables"
    echo -e "\t-prod options generate an empty database"
    echo "To remove files in Traces, Downloads, and Runs use destroy on production"
}

remove-files() {
  rm -rf Traces/*
  rm -rf Downloads/*
  rm -rf Runs/*
}

if [ $# -ne 1 ]; then
    usage
    exit 1
fi

case $1 in
  "setup-dev")
    if [ -e "var/openivn.sqlite3" ]
    then
        echo "Error: database already exists"
    else
        mkdir -p var/
        sqlite3 var/openivn.sqlite3 < sql/schema.sql
        sqlite3 var/openivn.sqlite3 < sql/data.sql
    fi
    ;;

  "setup-prod")
    if [ -e "var/openivn.sqlite3" ]
    then
        echo "Error: database already exists"
    else
        mkdir -p var/
        sqlite3 var/openivn.sqlite3 < sql/schema.sql
    fi
    ;;

  "destroy")
    remove-files
    rm -rf var/openivn.sqlite3
    ;;

  "reset-dev")
    rm -f var/openivn.sqlite3
    mkdir -p var/
    sqlite3 var/openivn.sqlite3 < sql/schema.sql
    sqlite3 var/openivn.sqlite3 < sql/data.sql
    ;;

  "reset-prod")
    rm -f var/openivn.sqlite3
    mkdir -p var/
    sqlite3 var/openivn.sqlite3 < sql/schema.sql
    ;;

  "dump")
    if [ ! -e "var/openivn.sqlite3" ]
    then
        echo "Error: database doesn't exist"
    else
        echo "users"
        echo "-------------------------------------------"
        sqlite3 -column -header var/openivn.sqlite3 'SELECT * FROM users'
        echo ""
        echo ""
        echo "apps"
        echo "-------------------------------------------"
        sqlite3 -column -header var/openivn.sqlite3 'SELECT * FROM apps'
        echo ""
        echo ""
        echo "permissions"
        echo "-------------------------------------------"
        sqlite3 -column -header var/openivn.sqlite3 'SELECT * FROM permissions'
        echo ""
        echo ""
        echo "vehicles"
        echo "-------------------------------------------"
        sqlite3 -column -header var/openivn.sqlite3 'SELECT * FROM vehicles'
        echo ""
        echo ""
        echo "traces"
        echo "-------------------------------------------"
        sqlite3 -column -header var/openivn.sqlite3 'SELECT * FROM traces'
        echo ""
        echo ""
        echo "developer_messages"
        echo "-------------------------------------------"
        sqlite3 -column -header var/openivn.sqlite3 'SELECT * FROM developer_messages'
        echo ""
    fi
    ;;
  *)
    usage
    exit 1
    ;;
esac
