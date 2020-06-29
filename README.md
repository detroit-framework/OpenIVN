# OpenIVN

Welcome to our repo.

# Table of Contents
- [Server Setup](#Server-Setup)
- [Streaming](#Streaming)
- [API Documentation](#API-Documentation)
- [Development Details](#Development-Details)

# Variables
Replace the following variables with the appropriate values.
* Replace `SERVER-URL` in README.md with the URL of your server.
* Update the value of `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in openivn/\_\_init\_\_.py with your Google Client ID and Client Secret to enable Google account authentication.

# Server Setup

1. Install Nginx (at least version 1.14.0)
    ```bash
   # install nginx
   $ sudo apt install nginx
   
   # check version
   $ nginx -v
   ```
    
    Replace the following files with the provided data.
    
   `/etc/nginx/nginx.conf`
   ```bash
    user www-data;
    worker_processes 1;
    pid /run/nginx.pid;

    events {
	    worker_connections 1024;
    }

    http {
        ##
        # Basic Settings
        ##
        sendfile on;
        tcp_nopush on;
        tcp_nodelay on;
        keepalive_timeout 65;
        types_hash_max_size 2048;

        include /etc/nginx/mime.types;
        default_type application/octet-stream;

        ##
        # SSL Settings
        ##
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2; # Dropping SSLv3, ref: POODLE
        ssl_prefer_server_ciphers on;
    
        ##
        # Logging Settings
        ##
        access_log /var/log/nginx/access.log;
        error_log /var/log/nginx/error.log;
    
        ##
        # Gzip Settings
        ##
        gzip on;
        gzip_disable "msie6";
    
        ##
        # Virtual Host Configs
        ##
        include /etc/nginx/conf.d/*.conf;
        include /etc/nginx/sites-enabled/*;
    }
   ```
   
   `/etc/nginx/proxy_params`
   ```bash
   proxy_set_header Host $http_host;
   proxy_set_header X-Real-IP $remote_addr;
   proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
   proxy_set_header X-Forwarded-Proto $scheme;
   ```
   
   `/etc/nginx/sites-available/default`
   Don't forget to replace `SERVER-URL` and add values for the `ssl_certificate` and `ssl_certificate_key` fields.
   ```bash
   server {
       listen 1609 ssl; #default_server;
       server_name SERVER-URL;
       
       client_max_body_size 50M;
       
       ssl on;
       ssl_certificate #path/to/your/ssl/cert/here;
       ssl_certificate_key #path/to/your/ssl/cert/key/here;
       
       location / {
           proxy_pass http://127.0.0.1:1610;
           include /etc/nginx/proxy_params;
       }
   
       location /robots.txt {
           return 200 "User-agent: *\nDisallow: /\n";
       }
   }
   ```

2. Clone this repo
    ```bash
    $ git clone https://github.com/username/name_of_this_repo.git
    $ cd OpenIVN
    ```
3. Set up virtual environment
    ```bash
    $ python3.8 -m venv env
    $ source env/bin/activate
    ```
4. Install dependencies
    ```bash
    $ pip install --upgrade pip setuptools wheel
    $ pip install -e .
    ```
5. Setup database

    You'll need to setup the database before running the server. If you want dummy data run `./bin/database.sh setup-dev`. If you want the prod-ready version without dummy data run `./bin/database.sh setup-prod`. Check out the database.sh script to view additional functionality.
    
6. Run Flask development server
    ```bash
    $ ./bin/server.sh start-dev
    ```
    Might need to make the script an executable: `chmod +x bin/server.sh`
   
    Sanity check
    ```bash
   $ curl http://localhost:1609/api/v1/hello_world/
   $ curl https://SERVER-URL:1609/api/v1/hello_world/
   ```
   
   Both requests should produce the same response:
   ```json
   {
     "message_text": "Hello world!",
     "url": "/api/v1/hello_world/"
   } 
   ```

7.  Run Nginx/Gunicorn production server

    Note: stop the development server before starting the production server (`./bin/server.sh stop-dev`)
    ```bash
    $ ./bin/server.sh start-prod
    ```
    Note: you will need `sudo` access to start Nginx server.  
    Might need to make the script an executable: `chmod +x bin/server.sh`
    
    Sanity check (Note the updated localhost port - 1610)
    ```bash
    $ curl http://localhost:1610/api/v1/hello_world/
    $ curl https://SERVER-URL:1609/api/v1/hello_world/
    ```

    Both requests should produce the same response:
    ```json
    {
    "message_text": "Hello world!",
    "url": "/api/v1/hello_world/"
    }
    ```

### Notes:
* Generate a new API key for each additional device that wants to make requests to our endpoint by running `openivn/utilities/generate_api_key.py`. Add key on a new line to the file in `openivn/api.key`
* You also need to generate a secret key for the flask config, run `python3 -c "import os; print(os.urandom(24))"` and add the key to line 16 in `openivn/config.py`
* Use HTTPS to connect to server
* Occasionally, you will need to manually kill Gunicorn. This may be necessary when running the stop-dev command doesn't work.
```bash
$ ps ax | grep gunicorn
$ sudo kill <PID>
```
* You will need to provide your own CAN bus reverse engineering solution in order to use the generate DBC endpoint. To integrate with OpenIVN, call your code from within generate_dbc.py, and update the dbc status when reverse engineering is complete. Files are organized within the run folder (make model year) as follows:
```
make_model_year/
    OBD.csv
    Phase1.json
    Events/
        AC_FAN_ON.json
        AC_FAN_SPEED_DOWN.json
        ...
```


# Streaming

### UDP
* Packets sent from mobile app to OpenIVN in **regular mode** will be formatted as:
```text
app_id, vehicle_str, timestamp, can_id, bus_id, payload

1,Make_Model_Year_Wheelbase,1582154787.243,359,2,727f010000190900
```

* Packets sent from mobile app to OpenIVN in **buffered mode** will be formatted as:  
    * Note that the data in { } will be repeated a variable number of times
```text
app_id, vehicle_str, {timestamp, can_id, bus_id, payload}

1,Make_Model_Year_Wheelbase,1582154787.243,359,2,727f010000190900,1582154787.255,359,2,727f010000190901,1582154787.289,359,2,727f010000190922
```


* Packets sent from OpenIVN to the developer will be formatted as:  
```text
{
  'app_id': 1,
  'vehicle_str': 'Make_Model_Year_Wheelbase',
  'timestamp': 1582154787.243,
  'item': item,
  'data': trans_data
}
``` 

### TCP

* First packet sent from mobile app to OpenIVN will be formatted as:
```text
app_id, vehicle_str
```

* All subsequent packets sent from mobile app to OpenIVN will be formatted as:
```text
timestamp, can_id, bus_id, payload
```

* Packets sent from OpenIVN to the developer will be formatted as:
```text
TO BE DETERMINED (probably same as UDP, above)
```

* Packets sent from Developer to OpenIVN will be formatted as:  
(Note: this will be the same format that will be sent to the mobile app.)
```text
{
    "app_id": 1,
    "message": "Message to be displayed to user."
}
```

# API Documentation

### Hello World

`https://SERVER-URL:1609/api/v1/hello_world/`

```json
{
  "message_text": "Hello world!",
  "url": "/api/v1/hello_world/"
}
```

### Get developer message

`https://SERVER-URL:1609/api/v1/messages/<int:app_id>`

```json
{
  "app_id": 1,
  "message": "Message from developer.",
  "timestamp": "2020-03-19 12:13",
  "url": "/api/v1/messages/1"
}
```

### Get VIN

`https://SERVER-URL:1609/api/v1/vin/<string:vin>`

```json
{
  "make": "MAKE",
  "model": "MODEL",
  "trim_options": [
    {
      "default": true,
      "trim": "2000 Sample Car",
      "trim_id": "000001"
    },
    {
      "default": false,
      "trim": "2001 Sample Car",
      "trim_id": "000002"
    },
    {
      "default": false,
      "trim": "2002 Sample Car",
      "trim_id": "000003"
    }
  ],
  "url": "/api/v1/vin/SAMPLE_VIN_NUMBER",
  "wheelbase": 100,
  "year": "2000"
}
```

### Get App List

`https://SERVER-URL:1609/api/v1/apps/`

```json
{
  "apps": [
    {
        "author_id": "001",
        "author_name": "George Washington",
        "description": "Knowledge is in every country the surest basis of public happiness.",
        "id": 1,
        "name": "America101",
        "streaming": 0,
        "url": "/api/v1/apps/1/"
    },
    {
        "author_id": "002",
        "author_name": "John Adams",
        "description": "I read my eyes out and can’t read half enough neither. The more one reads the more one sees we have to read.",
        "id": 2,
        "name": "Prez2",
        "streaming": 1,
        "url": "/api/v1/apps/2/"
    },
    {
        "author_id": "003",
        "author_name": "Thomas Jefferson",
        "description": "On matters of style, swim with the current, on matters of principle, stand like a rock.",
        "id": 3,
        "name": "Declaration",
        "streaming": 0,
        "url": "/api/v1/apps/3/"
    },
    {
        "author_id": "004",
        "author_name": "James Madison",
        "description": "Philosophy is common sense with big words.",
        "id": 4,
        "name": "Bill-o-Rights",
        "streaming": 1,
        "url": "/api/v1/apps/4/"
    },
  ],
  "url": "/api/v1/apps/"
}
```

### Get App

`https://SERVER-URL:1609/api/v1/apps/<int:app_id_slug>/`

```json
{
  "author_id": "001",
  "author_name": "George Washington",
  "description": "Knowledge is in every country the surest basis of public happiness.",
  "id": 1,
  "name": "America101",
  "permissions": {
    "Acceleration Sensors": true,
    "Battery": true,
    "Doors": true,
    "Engine Information": true,
    "Engine Utilization": true,
    "Fuel Information": true,
    "Gyroscope": true,
    "HVAC": true,
    "Hood": true,
    "Horn": true,
    "Lights": true,
    "Mirrors": true,
    "Parking Brake": true,
    "Pedal Positions": true,
    "Position Information": true,
    "Seat Belts": true,
    "Speed": true,
    "Torque": true,
    "Trunk": true,
    "Turn Signals": true,
    "Windows": true,
    "Windshield Wipers": true
  },
  "streaming": 0,
  "url": "/api/v1/apps/1/"
}
```

### Translate
`https://SERVER-URL:1609/api/v1/translate/?make=Make&model=Model&year=Year&wheelbase=Wheelbase&app_id=1&username=JohnDoe`

#### query params (url parameters)

make

model

year

wheelbase

app_id

user_id

#### Form Body

zip_file: translate.zip Contains <untranslated.json>

```json
{
    "status": "Translated and saved",
    "url": "/api/v1/translate/"
}
```

# Development Details

* Server: SERVER-URL
* Ports:
    * 1609: TCP, handles HTTPS access to website
    * 1610: TCP, Gunicorn (internal) 
    * 1611: UDP, receives vehicular data in online mode
    * 1612: TCP, receives vehicular data in online mode
    * 1616: TCP, receives message data from developers intended for mobile app users
* External webserver (reverse proxy): Nginx
* Internal webserver (WSGI): Gunicorn
