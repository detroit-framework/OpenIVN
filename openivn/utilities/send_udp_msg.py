import socket
import json
import openivn
import logging


def send_udp_msg(data_dict):
    """
    Translate a message from the job queue and send using UDP.

    Args:
        data_dict (dict): Data needed to send message.
    """
    # Save message to a file for testing purposes
    with open(openivn.UDP_TEST_FILE, 'a') as outfile:
        json.dump(data_dict['data'], outfile)
        outfile.write('\n')

    # Create a INET, STREAMing UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((data_dict['host'], data_dict['port']))

    # Send message
    sock.sendall(json.dumps(data_dict['data']).encode('utf-8'))
    sock.close()
