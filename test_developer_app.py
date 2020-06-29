import socket
import json


def sample_app(app_id, echo_frequency):
    """
    Sample developer app for DETROIT.

    Receives online streaming data from OpenIVN and replies with a message
    every echo_frequency number of messages.

    Args:
        app_id: (int) ID corresponding to this particular app in OpenIVN DB.
        echo_frequency: (int) number of messages that are received before a
            message is echoed back to DETROIT.
    """
    app_host = "0.0.0.0"
    app_port = 1678

    # Create an INET, STREAMing TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((app_host, app_port))
    sock.settimeout(1)  # accept(), recv() will block for max of 1s
    sock.listen(5)

    # Listen for new connections forever
    while True:
        # Connect to DETROIT
        try:
            client_socket, address = sock.accept()
            messages_received = 0
        except socket.timeout:
            continue
        print(f"TCP connection from DETROIT at {address[0]}, "
              f"port {address[1]}")

        # Loop until DETROIT closes connection
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
            # print(f"From DETROIT: {decoded_data}")
            print("Received a message from DETROIT")
            messages_received += 1

            # Send message to DETROIT to forward to front end app
            # every 200 messages I receive
            if (messages_received % echo_frequency) == 0:
                message_dict = {
                    'app_id': app_id,
                    'message': f'Test message from developer after receiving '
                               f'{messages_received} messages'
                }
                try:
                    detroit_host = "127.0.0.1"
                    detroit_port = 1616
                    # Create a INET, STREAMing TCP socket
                    send_sock = socket.socket(socket.AF_INET,
                                              socket.SOCK_STREAM)
                    send_sock.connect((detroit_host, detroit_port))

                    # Send message
                    send_sock.sendall(json.dumps(message_dict).encode('utf-8'))
                    send_sock.close()

                    print(f"Sent Developer message to DETROIT at "
                          f"{detroit_host}, port {detroit_port}")

                except ConnectionRefusedError:
                    print(f"Could not connect to host {detroit_host} "
                          f"at port {detroit_port}")

        # Close connection when recv() returns empty data
        client_socket.close()
        print("DETROIT closed the connection")


if __name__ == '__main__':
    sample_app(app_id=6, echo_frequency=50)
