# Script to define useful functions

import data
import json


#  Import organisation_type_codelist as a global, then delete when used to save memory
with open('data/IATI-Codelists-2/out/clv2/json/en/OrganisationType.json') as fh:
    organisation_type_codelist = json.load(fh)
organisation_type_dict = {c['code']: c['name'] for c in organisation_type_codelist['data']}
del organisation_type_codelist


def get_publisher_type(publisher):
    """Return a dictionary of publisher organisation information, based on what is stored
       in CKAN for the given publisher registry ID.
       Returns None if publisher is not found.
    """

    # Check that the publisher is in the list of ckan_publishers
    if publisher not in data.ckan_publishers:
        return None

    # Get the code the organisation from CKAN data (this will be in line with the OrganisationType codelist)
    organization_type_code = data.ckan_publishers[publisher]['result']['publisher_organization_type']

    # Get the english language name of this organisation type, according to the codelist
    organization_type_name = organisation_type_dict[organization_type_code]

    # Return a dictionary with code and name
    return {'code': organization_type_code, 'name': organization_type_name}
