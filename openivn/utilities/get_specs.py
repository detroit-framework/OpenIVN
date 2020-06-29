import re
import requests
from bs4 import BeautifulSoup


def assemble_url(make, model, year, trim_id=None):
    """
    Assembles a URL to get data from Car and Driver's website.

    Args:
        make (str): Vehicle make.
        model (str): Vehicle model.
        year (str): Vehicle year.
        trim_id (str): Trim identifier, used by Car and Driver's website.

    Returns:
        url (str): URL used to make request.
    """

    base_url = "https://www.caranddriver.com"
    make = make.lower()
    model = model.lower()
    model.replace(" ", "-")
    make_and_model = "-".join((make, model))
    extra_stuff = "_".join((make, model, make_and_model, year))
    if trim_id:
        custom_url = "/".join((base_url, make, model, "specs", year,
                               extra_stuff, trim_id))
    else:
        custom_url = "/".join((base_url, make, model, "specs", year,
                               extra_stuff))

    return custom_url


def get_specs(make, model, year, trim_id=None):
    """
    Retrieves specs for a particular vehicle if a trim is specified, or
    retrieves generic specs and a list of trim options.

    Arguments:
        make (str): Vehicle make.
        model (str): Vehicle model.
        year (str): Vehicle year.
        trim_id (str): Trim identifier, used by Car and Driver's website.

    Returns:
        specs (dict): Key = spec name, value = specification value (float/str)

    Raises:
        Exception: if URL used to access Car and Driver's website is invalid
    """

    url = assemble_url(make, model, year, trim_id)

    # Get web page
    r = requests.get(url)
    if r.status_code != 200:
        error_text = "Car and Driver's website returned a {0} - {1}. " \
                     "URL was {2}".format(r.status_code, r.reason, url)
        raise Exception(error_text)

    # Convert downloaded page to structured HTML
    soup = BeautifulSoup(r.text, "html.parser")

    # Key = spec name
    # Value = specification value (float) if valid, otherwise NA
    specs = {
        "steering_ratio": 0.0,  # unknown unit
        "trim": '',
        "trim_options": []
    }

    # Determine trim name given a trim_id
    # Note: this data isn't necessary to have, but useful for displaying
    # to user in output
    if trim_id:
        # Find trim name
        for elt in soup.find_all("option", selected=True):
            # Use parent id to find the selected trim
            parent_id = elt.parent.get("id")
            if parent_id == "selectTrim":
                specs['trim'] = elt.text
                break
    # If no trim was provided, determine available style & trim options,
    # Also determine generic wheelbase (first option on website)
    else:
        style_options = []
        # Determine available style & trim options
        for elt in soup.find_all("option"):
            parent_id = elt.parent.get("id")
            if parent_id == "selectStyle":
                style_options.append(elt.text)
            elif parent_id == "selectTrim":
                # Store information related to this trim
                specs['trim_options'].append({
                    'trim': elt.text,
                    'trim_id': elt["value"],
                    'default': False
                })

        # Determine currently selected trim option
        for elt in soup.find_all("option", selected=True):
            # Use parent id to find the selected trim
            parent_id = elt.parent.get("id")
            if parent_id == "selectTrim":
                selected_trim = elt.text
                # Found the selected trim, update specs to reflect this info
                # Currently using linear search which is bad, however,
                # default is usually first item in list so it's okay
                for i in range(len(specs['trim_options'])):
                    if specs['trim_options'][i]['trim'] == selected_trim:
                        specs['trim_options'][i]['default'] = True
                        # After updating info, stop looking for value
                        break
                # Stop searching once the selected trim is found
                break

    # Extract desired vehicle specs
    for elt in soup.find_all("td"):
        if re.search("Steering Ratio", elt.text):
            # Check if text is a number
            if elt.next_sibling.text == "N/A":
                specs["steering_ratio"] = "NA"
            else:
                specs["steering_ratio"] = float(elt.next_sibling.text)
        elif re.search("Wheelbase", elt.text):
            # Check if text is a number
            if elt.next_sibling.text == "N/A":
                specs["wheelbase"] = "NA"
            else:
                specs["wheelbase"] = float(elt.next_sibling.text)

    return specs


if __name__ == '__main__':
    get_specs("Make", "Model", "2000")
