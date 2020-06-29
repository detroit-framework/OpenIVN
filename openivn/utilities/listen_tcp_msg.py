import socket
import openivn
import logging
import time
import sys
from collections import defaultdict
import json
import queue
import multiprocessing as mp
# from openivn.utilities.send_tcp_msg import send_tcp_msg
from openivn.utilities.decorators import get_time
from openivn.model import get_db


def send_tcp_msg(dest_host, dest_port, q, tcp_conn_time_start):
    # Create a INET, STREAMing TCP socket
    sending_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sending_sock.connect((str(dest_host), int(dest_port)))

    done_sending = False
    # Keep going until the None is seen
    while not done_sending:
        messages = []
        try:
            for _ in range(10):
                messages.append(q.get(False))
        except queue.Empty:
            pass
        # Check if the last thing is none
        if messages and not messages[-1]:
            messages.pop()
            done_sending = True
        # send the message if it got one
        if messages and messages[0]:
            # logging.info("sending: " + str(messages))
            sending_sock.sendall(json.dumps(messages).encode('utf-8'))
    sending_sock.close()
    time_end = time.time()
    logging.info(f"TCP TIMING: Done Sending all data "
                 f"{get_time(time_end - tcp_conn_time_start)}")


def listen_tcp_msg(app):
    """Receive a TCP message and add to the job queue."""
    with app:
        server_host = "0.0.0.0"
        server_port = 1612

        # Create an INET, STREAMing TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server_host, server_port))
        sock.settimeout(1)  # accept(), recv() will block for max of 1s
        sock.listen(5)

        # Set up access to database
        db = get_db()

        # create a special Buffer Structure
        buff = Buff(',')
        # Listen for new connections forever
        while True:
            # Set up a connection
            try:
                client_socket, address = sock.accept()
            except socket.timeout:
                continue
            logging.info(f"TCP connection from {address[0]}")
            # Start timer for TCP connection
            tcp_conn_time_start = time.time()

            app_id = None
            vehicle_str = None
            permissions = None
            # Counter for the cumulative size of all TCP segments received,
            # measured in bytes
            tcp_data_size = 0

            # Measure number of CAN messages that were added to the queue
            # and then sent to the developer
            trans_msg = 0
            total_msg = 0

            # Loop until client closes connection
            while True:
                try:
                    data = client_socket.recv(4096)
                    last_message = time.time()
                except socket.timeout:
                    continue
                if not data:
                    # When client closes the connection, recv() returns
                    # empty data, which breaks out of the loop
                    # Assume that client will always close the connection

                    # Log amount of data sent during this transmission
                    logging.info(f"Amount of data received: "
                                 f"{tcp_data_size} bytes")

                    # Exit loop
                    break

                # Record size of packet, add header size
                tcp_data_size += (sys.getsizeof(data) + 43)

                # Go from bytes to string
                decoded_data = data.decode('utf-8')

                # First packet contains app_id and vehicle_str
                if not app_id and not vehicle_str:
                    try:
                        app_id, vehicle_str = decoded_data.split(',')

                        logging.info(f"Connection for app {app_id} for {vehicle_str}")

                        # Cast to appropriate type needed for DB access
                        app_id = int(app_id)

                        # Store IP address of front end app so we can send
                        # a message from the developer
                        store_sql_command = "UPDATE apps SET frontend_ip = ? WHERE app_id = ?"
                        db.execute(store_sql_command, (address[0], app_id))
                        db.commit()

                        # Use app ID to determine host and port for message delivery
                        endpoint_url = db.execute(
                            "SELECT * FROM apps WHERE app_id = ?", (app_id,)
                        ).fetchone()['stream_endpoint']
                        dest_host, dest_port = endpoint_url.split(":")

                        # TODO: remove testing data
                        # dest_host = '127.0.0.1'
                        # dest_port = 1699

                        # create a MP Queue
                        send_q = mp.Queue()
                        # Add the Vehicle_str and app_id to developer
                        send_q.put({"vehicle_str": vehicle_str, "app_id": app_id})
                        # start the process
                        sender = mp.Process(target=send_tcp_msg,
                                            args=(dest_host, dest_port, send_q, tcp_conn_time_start),)
                        # start the sender
                        sender.daemon = True
                        logging.info("Starting sender")
                        sender.start()

                        # Determine permissions based on app ID
                        permissions = openivn.api.translate.permissions_helper(app_id)

                        logging.info(f"Permissions for app {app_id} are {permissions}")

                        # Load DBC based on vehicle string
                        if vehicle_str not in openivn.GLOBAL_DBC:
                            logging.info("DBC Loading")
                            openivn.GLOBAL_DBC[
                                vehicle_str] = openivn.api.translate.dbc_helper(vehicle_str)

                        # create reverse lookup of id_dbc to entry
                        dbc = defaultdict(list)
                        for val in openivn.GLOBAL_DBC[vehicle_str].values():
                            dbc[str(val["ID"]) + '_' + str(val["DBC"])].append(val)
                        logging.info("DBC Loaded")

                        # Log data for testing purposes
                        # with open(openivn.TCP_TEST_FILE, 'a') as outfile:
                        #     outfile.write(f"Connection for app {app_id} "
                        #                   f"for {vehicle_str}\n")

                    except ValueError as v_error:
                        # Catch errors when not enough values were provided
                        logging.error(f"{v_error} with "
                                      f"data={decoded_data.strip()}")
                        continue
                else:
                    # If we've already identified the app and vehicle,
                    # then we assume the rest of the packets for this
                    # connection will be vehicular data
                    try:
                        # logging.info(f"decoded_data={decoded_data}")
                        # Splitting for a single tuple per packet
                        # timestamp, can_id, bus_id, payload = decoded_data.split(',')

                        # add the items to the buffer
                        buff += decoded_data
                        # List of tuples, one for each data packet
                        # (timestamp, can_id, bus_id, payload)
                        for timestamp, can_id, bus_id, payload in buff:
                            # Translate data using DBC and permissions
                            total_msg += 1
                            data_points = {}

                            # check if id_dbc is in our reverse mapping
                            lookup = str(can_id) + '_' + str(bus_id)
                            if lookup in dbc:
                                entry = dbc[lookup]
                                for e in entry:
                                    data_points[e["column"]] = openivn.api.translate.translate(payload,
                                                                                               e["Start"],
                                                                                               e["End"],
                                                                                               e["Coefficient"],
                                                                                               e["Intercept"])
                            message = {
                                "timestamp": timestamp,
                                "data": data_points
                            }
                            if not data_points:
                                continue
                            # add the message the queue
                            send_q.put(message)

                            trans_msg += 1

                            # logging.info(f'Remaining unprocessed Buffer {buff}')

                    except ValueError as v_error:
                        # Catch errors when not enough values were provided
                        logging.error(f"{v_error} with "
                                      f"data={decoded_data.strip()} "
                                      f"Buffer contains {buff}")
                        continue

            # Close connection when recv() returns empty data
            client_socket.close()
            # add None to send_q to let it know its done
            send_q.put(None)
            # Wait until the sender is done
            sender.join()

            # Log number of CAN messages
            end_time = time.time()
            logging.info(f"Translated and Sent {trans_msg} out of {total_msg} Total Messages. "
                         f"for app {app_id}, vehicle {vehicle_str.strip()}")
            logging.info(f"TCP TIMING Last Message Delta {get_time(end_time-last_message)}")

            # Write to file that connection was closed
            # with open(openivn.TCP_TEST_FILE, 'a') as outfile:
            #     outfile.write('========== Connection closed ==========\n')


class Buff:
    """
    This data structure can take in a delimited string and continually yield only n number
    of values from that delimited string.
    """
    def __init__(self, char):
        """Initialize a buffer. Char is the deliminator and num is the amount of items"""
        self.x = ''
        self.char = char
        self.num = 4

    def __repr__(self):
        """for debugging purposes."""
        return self.x

    def __iadd__(self, other):
        """Add items into the buffer"""
        self.x += other.replace('\n', '')
        return self

    def __iter__(self):
        """Create an iterator object."""
        return self

    def __next__(self):
        """Determine when the buffer should not yield any more values."""
        split_loc = []
        for i, c in enumerate(self.x):
            if c == self.char:
                split_loc.append(i)
            if len(split_loc) == self.num:
                return self.next(split_loc)
        raise StopIteration

    def next(self, split_loc):
        """This function is called to get the next items in the buffer."""
        # get the 4 items
        timestamp = self.x[:split_loc[0]]
        can_id = self.x[split_loc[0]+1:split_loc[1]]
        bus_id = self.x[split_loc[1]+1:split_loc[2]]
        payload = self.x[split_loc[2]+1:split_loc[3]]
        # remove them from x
        self.x = self.x[split_loc[3] + 1:]
        # return them
        yield from [timestamp, int(can_id), int(bus_id), payload]

