import openivn
import requests


def get_google_provider_config():
    """
    Retrieve Google provider configuration document.

    :return: JSON string with info about Google's provider configuration.
    """
    return requests.get(openivn.GOOGLE_DISCOVERY_URL).json()
