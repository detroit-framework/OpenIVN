import socket
import json
import logging
import time
from openivn.model import get_db
from openivn.utilities.decorators import get_time


def tcp_reverse_flow(app):
    """Forward messages from developer to Android app via TCP."""
    with app:
        server_host = "0.0.0.0"
        server_port = 1616

        # Set up access to database
        db = get_db()

        # Create an INET, STREAMing TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server_host, server_port))
        sock.settimeout(1)  # accept(), recv() will block for max of 1s
        sock.listen(5)

        # Listen for new connections forever
        while True:
            # Connect to developer
            try:
                client_socket, address = sock.accept()
            except socket.timeout:
                continue
            logging.info(f"TCP connection from Developer at {address[0]}")

            # Loop until Developer closes connection
            while True:
                try:
                    data = client_socket.recv(4096)
                except socket.timeout:
                    continue
                if not data:
                    # When client closes the connection, recv() returns
                    # empty data, which breaks out of the loop
                    # Assume that client will always close the connection
                    # Exit loop
                    break

                # Go from bytes to string
                decoded_data = data.decode('utf-8')
                decoded_data = decoded_data.strip()
                logging.info("Received message from Developer")
                logging.info(f"Message content: {decoded_data}")

                # Convert JSON message to dictionary
                try:
                    message_dict = json.loads(decoded_data)
                except json.JSONDecodeError:
                    logging.info("Invalid JSON message received. "
                                 "Message ignored.")
                    continue

                # Not taking any chances with app_id not being an integer
                message_dict['app_id'] = int(message_dict['app_id'])

                # Add message to database for frontend to retrieve
                sql_command = "SELECT COUNT(*) FROM developer_messages " \
                              "WHERE app_id = ?"
                # Get count from dictionary returned from database query
                result = db.execute(sql_command,
                                    (message_dict['app_id'],)
                                    ).fetchone()['COUNT(*)']

                if result == 0:
                    # App hasn't received a message from a developer yet
                    sql_command = "INSERT INTO developer_messages(app_id, " \
                                  "message) VALUES(?, ?)"
                    db.execute(sql_command, (message_dict['app_id'],
                                             message_dict['message']))
                else:
                    # Update message from developer
                    sql_command = "UPDATE developer_messages SET message = ? "\
                                  "WHERE app_id = ?"
                    db.execute(sql_command, (message_dict['message'],
                                             message_dict['app_id']))
                db.commit()
                logging.info("Added Developer message to database (committed)")

                # # Get IP address for this app
                # sql_command = "SELECT frontend_ip FROM apps WHERE app_id = ?"
                # mobile_host = db.execute(sql_command,
                #                          (message_dict['app_id'],)).fetchone()
                # mobile_host = str(mobile_host['frontend_ip'])
                # mobile_port = 1620  # Port is same for all apps
                # logging.info(f"Creating TCP socket with mobile app, host = {mobile_host}, port = {mobile_port}")
                #
                # # Send message to Android app
                # try:
                #     # Create a INET, STREAMing TCP socket
                #     send_sock = socket.socket(socket.AF_INET,
                #                               socket.SOCK_STREAM)
                #     send_sock.connect((mobile_host, mobile_port))
                #     logging.info("Connected to mobile")
                #
                #     # Send message
                #     send_sock.sendall(json.dumps(message_dict).encode('utf-8'))
                #     logging.info("Send data to mobile app")
                #     send_sock.close()
                #     logging.info("Closed socket with mobile app")
                #
                #     logging.info(f"Sent Developer message to App "
                #                  f"{message_dict['app_id']} at {mobile_host}, "
                #                  f"port {mobile_port}")
                #
                # except ConnectionRefusedError:
                #     logging.info(f"{__name__}: Could not connect to host "
                #                  f"{mobile_host} at port {mobile_port}")

            # Close socket to developer
            client_socket.close()
            logging.info("Closed socket with developer")


if __name__ == '__main__':
    tcp_reverse_flow()
