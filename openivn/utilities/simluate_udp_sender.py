import os
import socket


def simulate_udp_sender(file_path):
    """
    Simulate Android app for testing purposes.

    Args:
        file_path: path to file with UDP messages formatted as
                    app_id, vehicle_str, timestamp, can_id, bus_id, payload
    """
    host = '127.0.0.1'
    port = 1611

    # Create a INET, STREAMing UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((host, port))

    # Send one UDP message per line
    with open(file_path, 'r') as f:
        for message in f:
            sock.sendall(message.strip().encode('utf-8'))

    sock.close()


if __name__ == '__main__':
    test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests', 'long_test.txt')
    simulate_udp_sender(test_file)
