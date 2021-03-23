import json
import data
import csv
from collections import defaultdict
from itertools import zip_longest


def codelist_dict(codelist_path):
    codelist_json = json.load(open(codelist_path))
    return {c['code']: c['name'] for c in codelist_json['data']}


organisation_type_dict = codelist_dict('data/IATI-Codelists-2/out/clv2/json/en/OrganisationType.json')
country_dict = codelist_dict('data/IATI-Codelists-2/out/clv2/json/en/Country.json')
region_dict = codelist_dict('data/IATI-Codelists-2/out/clv2/json/en/Region.json')

aggregated_publisher = data.JSONDir('./stats-calculated/current/aggregated-publisher/')

activities_by = defaultdict(lambda: defaultdict(int))
publishers_by = defaultdict(lambda: defaultdict(int))

for publisher, publisher_data in aggregated_publisher.items():
    if publisher in data.ckan_publishers:
        organization_type = data.ckan_publishers[publisher]['result']['publisher_organization_type']
        # activities_by['type'][organisation_type_dict[organization_type]] += publisher_data['activities']
        publishers_by['type'][organisation_type_dict[organization_type]] += 1

        publisher_country_code = data.ckan_publishers[publisher]['result']['publisher_country']
        if publisher_country_code in country_dict or publisher_country_code in region_dict:
            publishers_by['country'][country_dict.get(publisher_country_code) or region_dict.get(publisher_country_code)] += 1
        else:
            print('Unrecognised registry publisher_country code: ', publisher_country_code)
        activity_countries = publisher_data['codelist_values'].get('.//recipient-country/@code')
        if activity_countries:
            for code, count in activity_countries.items():
                if code and code in country_dict:
                    activities_by['country'][country_dict.get(code)] += count
        activity_regions = publisher_data['codelist_values'].get('.//recipient-region/@code')
        if activity_regions:
            for code, count in activity_regions.items():
                if code and code in region_dict:
                    activities_by['region'][region_dict.get(code)] += count
    else:
        print('Publisher not matched:', publisher)

fieldnames = ['publisher_type', 'publishers_by_type', '', 'publisher_country', 'publishers_by_country', '', 'date', 'publishers_quarterly', '', 'activity_country', 'activities_by_country', '', 'activity_region', 'activities_by_region' ]

publishers_quarterly = []
publishers_by_date = json.load(open('./stats-calculated/gitaggregate-dated/publishers.json'))
for date, publishers in sorted(publishers_by_date.items()):
    if (date[8:10] == '30' and date[5:7] in ['06', '09']) or (date[8:10] == '31' and date[5:7] in ['03', '12']):
        publishers_quarterly.append((date, publishers))

with open('out/speakers_kit.csv', 'w') as fp:
    writer = csv.DictWriter(fp, fieldnames)
    writer.writeheader()
    sort_second = lambda x: sorted(x, key=lambda y: y[1], reverse=True)
    for publishers_by_type, publishers_by_country, publishers_quarterly_, activities_by_country, activities_by_region in zip_longest(
            sort_second(publishers_by['type'].items()),
            sort_second(publishers_by['country'].items()),
            publishers_quarterly,
            sort_second(activities_by['country'].items()),
            sort_second(activities_by['region'].items()),
    ):
        writer.writerow({
            'publisher_type': publishers_by_type[0] if publishers_by_type else '',
            'publishers_by_type': publishers_by_type[1] if publishers_by_type else '',
            'publisher_country': publishers_by_country[0] if publishers_by_country else '',
            'publishers_by_country': publishers_by_country[1] if publishers_by_country else '',
            'date': publishers_quarterly_[0] if publishers_quarterly_ else '',
            'publishers_quarterly': publishers_quarterly_[1] if publishers_quarterly_ else '',
            'activity_country': activities_by_country[0] if activities_by_country else '',
            'activities_by_country': activities_by_country[1] if activities_by_country else '',
            'activity_region': activities_by_region[0] if activities_by_region else '',
            'activities_by_region': activities_by_region[1] if activities_by_region else '',
        })
