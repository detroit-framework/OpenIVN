import requests
import json


def vin_lookup(vin):
    """
    Retrieves car information using VIN.

    Arguments:
        vin (str): Vehicle Identification Number.

    Returns:
        data (dict): Car information in key, value pairs

    Raises:
        Exception: if NHTSA API request returns an error or if there is
            an error with the VIN
    """
    # Make request
    url = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVINValuesBatch/"
    post_fields = {
        'format': 'json',
        'data': vin
    }
    response = requests.post(url, data=post_fields)
    if response.status_code != 200:
        error_text = "NHTSA API did not respond successfully."
        error_text += " NHTSA API returned a {0}".format(response.status_code)
        raise Exception(error_text)

    # Parse response data
    json_data = json.loads(response.text)

    # Check data to ensure VIN was valid
    # NHTSA will alert us if VIN is invalid, too short, malformed, etc
    error_code = json_data["Results"][0]["ErrorCode"]
    if error_code != "0":
        error_text = json_data["Results"][0]["ErrorText"]
        raise Exception(error_text)

    # Extract & store data from response
    data = {
        "make": json_data["Results"][0]["Make"],
        "model": json_data["Results"][0]["Model"],
        "model_year": json_data["Results"][0]["ModelYear"]
    }

    return data


if __name__ == '__main__':
    vin_lookup("ABCDE123456789012")
