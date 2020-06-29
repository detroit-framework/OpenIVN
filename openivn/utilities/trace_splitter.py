import os
import math


def trace_splitter(file, num_new):
    """
    Split the provided trace into smaller, equally-sized trace files.

    If num_new = 4, then 4 new files are created, each with 25% of the original
    trace file. File 0 has the first 25%, File 1 has the next 25%, and so on.

    Args:
        file (string): Path to original trace file.
        num_new (int): Number of new traces to be created.
    """
    # Get file path and extension
    file_path, file_extension = os.path.splitext(file)

    # Get file name from path
    file_dir, file_name = os.path.split(file_path)

    # Get percentage for each file, used for file naming scheme
    percentage = 1.0 / float(num_new)

    # Create new files names
    new_files = [os.path.join(file_dir, f"{file_name}_{percentage * 100}%_{x}{file_extension}") for x in range(num_new)]

    # Count number of lines in original file
    line_count = 0
    with open(file, 'r') as f:
        for line in f:
            line_count += 1

    # Number of lines per file to equally split the original trace
    target_lines = math.floor(line_count / num_new)

    with open(file, 'r') as infile:
        for new_file in new_files:
            # Number of lines written to new file
            written_lines = 0

            # Write specified number of lines to the new file
            with open(new_file, 'w') as outfile:
                while written_lines < target_lines:
                    outfile.write(infile.readline())
                    written_lines += 1


if __name__ == '__main__':
    trace_1 = "trace1.json"
    trace_2 = "trace2.json"
    trace_splitter(trace_2, 4)
