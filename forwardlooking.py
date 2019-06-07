# This file converts raw forward-looking data to percentages

from data import publishers_ordered_by_title, get_publisher_stats, publisher_name
import datetime

# Create a variable with the current year as an integer
this_year = datetime.date.today().year

# Create a list containing three years: the current year and two following
years = map(str, range(this_year, this_year + 3))

# Set column groupings, to be displayed in the user output
column_headers = [
    'Current activities at the start of each year',
    'Current activities with budgets for each year',
    'Percentage of current activities with budgets'
]

def generate_row(publisher):
    """Generate forward-looking table data for a given publisher
    """

    # Store the data for this publisher as a new variable
    publisher_stats = get_publisher_stats(publisher)

    # Create a list for publisher data, and populate it with basic data
    row = {}
    row['publisher'] = publisher
    row['publisher_title'] = publisher_name[publisher]
    row['year_columns'] = [{}, {}, {}]
    row['budget_not_provided'] = False
    # Work with hierarchies
    by_hierarchy = publisher_stats['by_hierarchy']
    hierarchies_with_nonzero_budgets = [
        h for h, stats in by_hierarchy.items()
        if not all(x == 0 for x in stats['forwardlooking_activities_with_budgets'].values())
    ]

    # Flag if budgets on current activities are reported at more than one hierarchy
    row['flag'] = len(hierarchies_with_nonzero_budgets) > 1

    hierarchies_with_budget_not_provided = [
        h for h, stats in by_hierarchy.items()
        if not all(x == 0 for x in stats['forwardlooking_activities_with_budget_not_provided'].values())
    ]

    # Loop over each of the three years (i.e. this year and the following two years) to generate the statistics for the table
    for year in years:

        forwardlooking_budget = 'forwardlooking_activities_with_budgets'
        if(len(hierarchies_with_budget_not_provided) > 0):
            forwardlooking_budget = 'forwardlooking_activities_with_budget_not_provided'
            row['budget_not_provided'] = True
        # If 'forwardlooking_activities_current' and 'forwardlooking_activities_with_budgets' are both in the bottom hierarchy
        if 'forwardlooking_activities_current' in publisher_stats['bottom_hierarchy'] and forwardlooking_budget in publisher_stats['bottom_hierarchy'] :
            if len(hierarchies_with_nonzero_budgets) != 1:
                # If budgets are at more than one hierarchy (or no hierarchies), just use activities at all hierarchies
                row['year_columns'][0][year] = publisher_stats['forwardlooking_activities_current'].get(year) or 0
                row['year_columns'][1][year] = publisher_stats[forwardlooking_budget].get(year) or 0
            else:
                # Else, use the hierarchy which they are reported at
                row['year_columns'][0][year] = by_hierarchy[hierarchies_with_nonzero_budgets[0]]['forwardlooking_activities_current'].get(year) or 0
                row['year_columns'][1][year] = by_hierarchy[hierarchies_with_nonzero_budgets[0]][forwardlooking_budget].get(year) or 0

            if not int(row['year_columns'][0][year]):
                row['year_columns'][2][year] = '-'
            else:
                row['year_columns'][2][year] = int(round(float(row['year_columns'][1][year])/float(row['year_columns'][0][year])*100))
        else:
            # Else if either 'forwardlooking_activities_current' or 'forwardlooking_activities_with_budgets' are not in the bottom hierarchy, set data zero
            # This should only occur if a publisher has 0 activities
            row['year_columns'][0][year] = '0'
            row['year_columns'][1][year] = '0'
            row['year_columns'][2][year] = '-'

    return row


def table():
    """Generate forward-looking table data for every publisher and return as a generator object
    """

    # Loop over each publisher
    for publisher_title, publisher in publishers_ordered_by_title:
        # Return a generator object
        yield generate_row(publisher)
