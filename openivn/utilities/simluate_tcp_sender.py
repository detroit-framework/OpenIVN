import os
import time
import socket


def simulate_tcp_sender(file_path):
    """
    Simulate Android app for testing purposes.

    Args:
        file_path: path to file with TCP messages formatted as
                    First message:
                        app_id, vehicle_str
                    Subsequent messages:
                        timestamp, can_id, bus_id, payload
    """
    host = '127.0.0.1'
    port = 1612

    # Create an INET, STREAMing TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # TODO: check that this actually is how the data is sent from front end
    #  Need to be able to control amount of data in each packet in order to
    #  guarantee that backend listen_tcp_message() works reliably
    # Send one TCP message per line
    with open(file_path, 'r') as f:
        # Send first line (app_id, vehicle_str)
        sock.sendall(f.readline().strip().encode('utf-8'))

        time.sleep(0.1)

        # Send the data (could be all in one message)
        for message in f:
            sock.sendall(message.strip().encode('utf-8'))
            time.sleep(.5)
            # Avoid compressing multiple lines into a single TCP packet
            # time.sleep(0.1)

    sock.close()


if __name__ == '__main__':
    test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                             'tests', '25_tcp_trace.txt')
    simulate_tcp_sender(test_file)
