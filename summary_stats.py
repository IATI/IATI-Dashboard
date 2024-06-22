# This file converts a range of transparency data to percentages

from data import publishers_ordered_by_title, get_publisher_stats, secondary_publishers
import common
import timeliness
import forwardlooking
import comprehensiveness
import coverage

# Set column groupings, to be displayed in the user output
columns = [
    # slug, header
    ('publisher_type', 'Publisher Type'),
    ('timeliness', 'Timeliness'),
    ('forwardlooking', 'Forward looking'),
    ('comprehensive', 'Comprehensive'),
    ('score', 'Score')
    ]


def is_number(s):
    """ @todo Document this function
    """
    try:
        float(s)
        return True
    except ValueError:
        return False

def convert_to_int(x):
    """ @todo Document this function
    """
    if is_number(x):
        return int(x)
    else:
        return 0


def table():
    """Generate data for the publisher forward-looking table
    """

    # Store timeliness data in variable
    timeliness_frequency_data = timeliness.publisher_frequency_dict()
    timeliness_timelag_data = timeliness.publisher_timelag_dict()

    # Loop over each publisher
    for publisher_title, publisher in publishers_ordered_by_title:

        # Store the data for this publisher as a new variable
        publisher_stats = get_publisher_stats(publisher)

        # Skip if all activities from this publisher are secondary reported
        if publisher in secondary_publishers:
            continue

        # Create a list for publisher data, and populate it with basic data
        row = {}
        row['publisher'] = publisher
        row['publisher_title'] = publisher_title
        row['publisher_type'] = common.get_publisher_type(publisher)['name']

        # Compute timeliness statistic
        # Assign frequency score
        # Get initial frequency assessment, or use empty set in the case where the publisher is not found
        frequency_assessment_data = timeliness_frequency_data.get(publisher, ())
        frequency_assessment = None if len(frequency_assessment_data) < 4 else frequency_assessment_data[3]
        if frequency_assessment == 'Monthly':
            frequency_score = 4
        elif frequency_assessment == 'Quarterly':
            frequency_score = 3
        elif frequency_assessment == 'Six-Monthly':
            frequency_score = 2
        elif frequency_assessment == 'Annual':
            frequency_score = 1
        else: # frequency_assessment == 'Less than Annual' or something else!
            frequency_score = 0

        # Assign timelag score
        # Get initial timelag assessment, or use empty set in the case where the publisher is not found
        timelag_assessment_data = timeliness_timelag_data.get(publisher, ())
        timelag_assessment = None if len(timelag_assessment_data) < 4 else timelag_assessment_data[3]
        if timelag_assessment == 'One month':
            timelag_score = 4
        elif timelag_assessment == 'A quarter':
            timelag_score = 3
        elif timelag_assessment == 'Six months':
            timelag_score = 2
        elif timelag_assessment == 'One year':
            timelag_score = 1
        else: # timelag_assessment == 'More than one year' or something else!
            timelag_score = 0

        # Compute the percentage
        row['timeliness'] = int( round((float(frequency_score + timelag_score) / 8) * 100))


        # Compute forward-looking statistic
        # Get the forward-looking data for this publisher
        publisher_forwardlooking_data = forwardlooking.generate_row(publisher)

        # Convert the data for this publishers 'Percentage of current activities with budgets' fields into integers
        numbers = [ int(x) for x in publisher_forwardlooking_data['year_columns'][2].itervalues() if is_number(x) ]
        
        # Compute and store the mean average for these fields
        row['forwardlooking'] = sum(int(round(y)) for y in numbers) / len(publisher_forwardlooking_data['year_columns'][2])


        # Compute comprehensive statistic
        # Get the comprehensiveness data for this publisher
        publisher_comprehensiveness_data = comprehensiveness.generate_row(publisher)

        # Set the comprehensive value to be the summary average for valid data
        row['comprehensive'] = convert_to_int(publisher_comprehensiveness_data['summary_average_valid'])


        # Compute score
        row['score'] = int( round(float(row['timeliness'] + row['forwardlooking'] + row['comprehensive']) / 3 ))

        # Return a generator object
        yield row
