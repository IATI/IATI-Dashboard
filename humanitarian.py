# This file builds a table to show humanitarian reporting for each publisher

from data import publishers_ordered_by_title, get_publisher_stats
import common

# Set column groupings, to be displayed in the user output
columns = [
    # slug, header
    ('publisher_type', 'Publisher Type'),
    ('num_activities', 'Number of activities'),
    ('publishing_humanitarian', 'Publishing humanitarian?'),
    ('humanitarian_attrib', 'Using humanitarian attribute?'),
    ('appeal_emergency', 'Appeal or emergency details'),
    ('clusters', 'Clusters'),
    ('timeliness', 'Timeliness (Commitment)'),
    ('average', 'Average')
    ]


def table():
    """Generate data for the humanitarian table
    """

    # Loop over each publisher
    for publisher_title, publisher in publishers_ordered_by_title:

        # Store the data for this publisher as a new variable
        publisher_stats = get_publisher_stats(publisher)

        # Create a list for publisher data, and populate it with basic data
        row = {}
        row['publisher'] = publisher
        row['publisher_title'] = publisher_title
        row['publisher_type'] = common.get_publisher_type(publisher)['name']

        # Get data
        row['num_activities'] = 'TBC'
        row['publishing_humanitarian'] = 'TBC'
        row['humanitarian_attrib'] = 'TBC'
        row['appeal_emergency'] = 'TBC'
        row['clusters'] = 'TBC'
        row['timeliness'] = 'TBC'
        row['average'] = 'TBC'

        # Return a generator object
        yield row
