from data import publishers_ordered_by_title, get_publisher_stats
import datetime

this_year = datetime.date.today().year
years = map(str, range(this_year, this_year+3))
column_headers = [ 
    'Current activities',
    'Current activities with budgets',
    'Percentage of current activities with budgets'
]

def table():
    for publisher_title, publisher in publishers_ordered_by_title:
        publisher_stats = get_publisher_stats(publisher)
        row = {}
        row['publisher'] = publisher
        row['publisher_title'] = publisher_title
        row['year_columns'] = [{},{},{}]

        by_hierarchy = publisher_stats['by_hierarchy']
        nonzero_budgets_by_hierachy = [
            (h, stats['forwardlooking_activities_with_budgets']) for h, stats in by_hierarchy.items()
            if not all(x==0 for x in stats['forwardlooking_activities_with_budgets'].values())
        ]
        # Flag if the list is not empty, and it contains more than the bottom hierarchy
        row['flag'] = (nonzero_budgets_by_hierachy != []) and (nonzero_budgets_by_hierachy[0][0] != max(by_hierarchy.keys()))


        for year in years:
            if 'forwardlooking_activities_current' in publisher_stats['bottom_hierarchy'] and 'forwardlooking_activities_with_budgets' in publisher_stats['bottom_hierarchy'] :
                row['year_columns'][0][year] = publisher_stats['bottom_hierarchy']['forwardlooking_activities_current'].get(year) or 0
                row['year_columns'][1][year] = publisher_stats['bottom_hierarchy']['forwardlooking_activities_with_budgets'].get(year) or 0
                if not int(row['year_columns'][0][year]):
                    row['year_columns'][2][year] = '-'
                else:
                    row['year_columns'][2][year] = int(round(float(row['year_columns'][1][year])/float(row['year_columns'][0][year])*100))
            else:
                # Should only occur if a publisher has 0 activities
                row['year_columns'][0][year] = '0'
                row['year_columns'][1][year] = '0'
                row['year_columns'][2][year] = '-'
        yield row

