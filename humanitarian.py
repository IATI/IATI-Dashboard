# This file builds a table to show humanitarian reporting for each publisher

from data import publishers_ordered_by_title, get_publisher_stats
import common

# Set column groupings, to be displayed in the user output
columns = [
    # slug, header
    ('publisher_type', 'Publisher Type'),
    ('num_activities', 'Number of Activities'),
    ('publishing_humanitarian', 'Publishing Humanitarian?'),
    ('humanitarian_attrib', 'Using Humanitarian Attribute?'),
    ('appeal_emergency', 'Appeal or Emergency Details'),
    ('clusters', 'Clusters'),
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

        # Get data from IATI-Stats output
        row['num_activities'] = publisher_stats.get('humanitarian', {}).get('is_humanitarian', '0')
        row['publishing_humanitarian'] = 100 if int(row['num_activities']) > 0 else 0

        # Calculate percentage of all humanitarian activities that are defined using the @humanitarian attribute
        row['humanitarian_attrib'] = (
            publisher_stats.get('humanitarian', {}).get('is_humanitarian_by_attrib', '0') / row['num_activities']
              if int(row['num_activities']) > 0 else 0
            ) * 100

        # Calculate percentage of all humanitarian activities that use the <humanitarian-scope> element to define an appeal or emergency
        row['appeal_emergency'] = (
            publisher_stats.get('humanitarian', {}).get('contains_humanitarian_scope', '0') / row['num_activities']
              if int(row['num_activities']) > 0 else 0
            ) * 100

        # Calculate percentage of all humanitarian activities that use clusters
        row['clusters'] = (
            publisher_stats.get('humanitarian', {}).get('uses_humanitarian_clusters_vocab', '0') / row['num_activities']
              if int(row['num_activities']) > 0 else 0
            ) * 100

        # Calculate the mean average
        row['average'] = (row['publishing_humanitarian'] + row['humanitarian_attrib'] + row['appeal_emergency'] + row['clusters']) / 4

        # Return a generator object
        yield row
