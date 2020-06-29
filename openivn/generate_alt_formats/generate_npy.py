"""Script to generate .npy container file for Python processing."""
import os
import json
import numpy as np


def generate_npy(filepath):
    """
    Converts a translated JSON trace to a NumPy container file.

    Args:
        filepath (str): path to JSON file

    Effects:
        Creates a file with the same name, but changes extension to .npy
    """
    # Get name of file, for using later to save file, but with .npy extension
    basename = os.path.basename(filepath)
    file_id, _ = basename.split('.')

    with open(filepath) as f:
        data = json.load(f)
        output_list = []
        for p in data:
            if data[p]['series'] != "Not In Trace":
                time_series = []
                data_series = []
                time_series.append(data[p]['base_timestamp'])
                for j in range(len(data[p]['series'])-1):
                    time_series.append(time_series[-1] + (1/(data[p]['sampling_freq'])))
                data_series = data[p]['series']
                output_list.append(np.column_stack((time_series, data_series)))
        np.save(f'Traces/{file_id}.npy', output_list, allow_pickle=True)
