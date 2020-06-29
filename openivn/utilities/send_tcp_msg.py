import socket
import json
import openivn
import logging
import time
from openivn.utilities.decorators import get_time


def send_tcp_msg(data_dict, tcp_conn_time_start):
    """
    Translate a message from the job queue and send using TCP.

    Args:
        data_dict (dict): Data needed to send message.
        tcp_conn_time_start (float): Time when TCP connection started.
    """
    # Save message to a file for testing purposes
    # with open(openivn.TCP_TEST_FILE, 'a') as outfile:
    #     json.dump(data_dict['data'], outfile)
    #     outfile.write('\n')

    try:
        # Create a INET, STREAMing TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((data_dict['host'], data_dict['port']))

        # Send message
        sock.sendall(json.dumps(data_dict['data']).encode('utf-8'))
        sock.close()
    except ConnectionRefusedError:
        logging.info(f"{__name__}: Could not connect to host {data_dict['host']} at port {data_dict['port']}")

    # Output timing info
    time_end = time.time()
    logging.info(f"TCP TIMING: "
                 f"{get_time(time_end - tcp_conn_time_start)}")
