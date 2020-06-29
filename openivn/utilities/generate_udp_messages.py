import os


def generate_udp_messages(file_path):
    """
    Creates a file that simulates UDP messages sent from the Android app.

    Args:
        file_path: path to trace file formatted as
                    timestamp, can_id,bus_id, payload
    """
    # Get file name from path
    file_dir, file_name = os.path.split(file_path)

    # Add UDP to file name
    file_name = f"udp_{file_name}"
    new_file_path = os.path.join(file_dir, file_name)

    # Dummy data
    app_id = '5'
    vehicle_str = 'Make_Model_2000_100'

    # Write data to file as it is being read in
    with open(new_file_path, 'w') as outfile:
        # Read in trace file
        with open(file_path, 'r') as infile:
            # Avoid reading entire file into memory cause it can be large
            for line in infile:
                timestamp, can_id, bus_id, payload = line.split(',')
                # Convert timestamp to milliseconds by inserting a '.'
                timestamp = timestamp[:-3] + '.' + timestamp[-3:]
                # Format and write data to file
                outfile.write(','.join([app_id, vehicle_str, timestamp, can_id, bus_id, payload]))


if __name__ == '__main__':
    generate_udp_messages('trace.txt')
