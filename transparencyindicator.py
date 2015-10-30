# This file converts a range of transparency data to percentages

from data import publishers_ordered_by_title, get_publisher_stats

def table():
    """Generate data for the publisher forward-looking table
    """

    # Loop over each publisher
    for publisher_title, publisher in publishers_ordered_by_title:

        # Store the data for this publisher as a new variable
        publisher_stats = get_publisher_stats(publisher)
        
        # Create a list for publisher data, and populate it with basic data
        row = {}
        row['publisher'] = publisher
        row['publisher_title'] = publisher_title

        # Store the coverage data
        row['coverage'] = publisher_stats['coverage']

        # Return a generator object
        yield row