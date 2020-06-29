import socket
import openivn
import logging
from redis import Redis
from rq import Queue
from openivn.utilities.send_udp_msg import send_udp_msg
from openivn.model import get_db


def listen_udp_msg(app):
    """Receive a UDP message and add to the job queue."""
    with app:
        server_host = "0.0.0.0"
        server_port = 1611

        # Create a INET, STREAMing UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((server_host, server_port))
        sock.settimeout(1)  # accept(), recv() will block for max of 1s

        # See https://python-rq.org/ for more details on how to use Redis & RQ
        q = Queue(connection=Redis())

        # Listen forever
        while True:
            # Accept UDP data
            try:
                data = sock.recv(4096)
            except socket.timeout:
                continue
            if data:
                data = data.decode('utf-8')

                try:
                    # Split data
                    app_id, vehicle_str, timestamp, can_id, bus_id, data = data.split(',')

                    # # TODO:Finish adapting this to handle multiple data packets
                    # split_data = data.split(',')
                    #
                    # # Data must be more than just app_id and vehicle_str.
                    # # app_id and vehicle_str must be accompanied by sets of
                    # # 4 additional items (timestamp, can_id, bus_id, data)
                    # if (len(split_data) > 2) and (
                    #         (len(split_data) - 2) % 4 == 0):
                    #     app_id = int(split_data[0])
                    #     vehicle_str = split_data[1]
                    #
                    #     # List of tuples, one for each data packet
                    #     # (timestamp, can_id, bus_id, data)
                    #     data_tuple_list = []
                    #     for i in range(2, len(split_data), 4):
                    #         data_tuple_list.append((split_data[i],
                    #                                 int(split_data[i + 1]),
                    #                                 int(split_data[i + 2]),
                    #                                 split_data[i + 3]))

                except ValueError as v_error:
                    # Catch errors when not enough values were provided
                    logging.error(f"{v_error} with data={data.strip()}")
                    continue

                # Cast data to appropriate types
                app_id = int(app_id)
                can_id = int(can_id)
                bus_id = int(bus_id)

                # Set up access to database
                db = get_db()

                # Use app ID to determine host and port for message delivery
                endpoint_url = db.execute(
                    "SELECT * FROM apps WHERE app_id = ?", (app_id,)
                ).fetchone()['stream_endpoint']
                dest_host, dest_port = endpoint_url.split(":")

                # Determine permissions based on app IDs
                permissions = openivn.api.translate.permissions_helper(app_id)

                # Load DBC based on vehicle string
                if vehicle_str not in openivn.GLOBAL_DBC:
                    openivn.GLOBAL_DBC[
                        vehicle_str] = openivn.api.translate.dbc_helper(
                        vehicle_str)
                        
                # TODO: adapt to fit multiple data packets
                # for data_tup in data_tuple_list:
                    # (timestamp, can_id, bus_id, data)

                # Translate data using DBC and permissions
                data_points = {}
                for p in permissions:
                    if p in openivn.GLOBAL_DBC[vehicle_str] and \
                            openivn.GLOBAL_DBC[vehicle_str][p]["ID"] == can_id and \
                            openivn.GLOBAL_DBC[vehicle_str][p]["DBC"] == bus_id:
                        # add the data to a dictionary
                        data_points[p] = openivn.api.translate.translate(data,
                                                                         openivn.GLOBAL_DBC[vehicle_str][p]["Start"],
                                                                         openivn.GLOBAL_DBC[vehicle_str][p]["End"],
                                                                         openivn.GLOBAL_DBC[vehicle_str][p]["Coefficient"],
                                                                         openivn.GLOBAL_DBC[vehicle_str][p]["Intercept"])

                # print(data_points)
                if not data_points:
                    # logging.info(f"Can ID {can_id} not a valid for permissions {permissions}")
                    continue

                # TODO: remove testing data
                # item = 'testing'
                # trans_data = 'YOOO'
                # dest_host = '0.0.0.0'  # TODO: replace with testing destination host
                # dest_port = 1612  # TODO: replace with testing destination port
                # Construct message to send to developer
                message = {
                    "app_id": app_id,
                    "vehicle_str": vehicle_str,
                    "timestamp": timestamp,
                    "data": data_points
                }
                # print(message)

                # Construct dictionary for the helper function to send to dev
                data_dict = {
                    "host": dest_host,
                    "port": int(dest_port),
                    "data": message,
                }

                q.enqueue(send_udp_msg, data_dict)

                # TODO: move up to here into the for loop to adapt for multiple data packets in buffered mode

        # This won't ever execute, but it's a reminder that we need to
        # close the socket if we ever decide to have some condition for the
        # while loop above.
        sock.close()
