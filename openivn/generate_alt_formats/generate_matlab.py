"""Script to generate .mat container file for MATLAB processing."""
import os
import json
import numpy as np
import scipy.io as scio


def generate_matlab(filepath):
    """
    Converts a translated JSON trace to a MATLAB container file.

    Args:
        filepath (str): path to JSON file

    Effects:
        Creates a file with the same name, but changes extension to .mat
    """
    # Get name of file, for using later to save file, but with .mat extension
    basename = os.path.basename(filepath)
    file_id, _ = basename.split('.')

    with open(filepath) as f:
        data = json.load(f)
        i = 0
        for p in data:
            if data[p]['series'] != "Not In Trace":
                i += 1
        obj_arr = np.zeros((i*2,), dtype=np.object)
        i = 0
        for p in data:
            if data[p]['series'] != "Not In Trace":
                time_series = []
                data_series = []
                time_series.append(data[p]['base_timestamp'])
                for j in range(len(data[p]['series'])-1):
                    time_series.append(time_series[-1] + (1/(data[p]['sampling_freq'])))
                data_series = data[p]['series']
                obj_arr[i] = p
                obj_arr[i+1] = np.column_stack((time_series, data_series))
                i += 2
        scio.savemat(f'Traces/{file_id}.mat', mdict={'translated': obj_arr})
