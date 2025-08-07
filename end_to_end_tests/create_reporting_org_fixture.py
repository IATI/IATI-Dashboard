import argparse
import json
import os
import uuid

parser = argparse.ArgumentParser()
parser.add_argument("reporting_org_short_name")
parser.add_argument("reporting_org_human_readable_name")
args = parser.parse_args()


with open(f"end_to_end_tests/fixtures/ckan/{args.reporting_org_short_name}", "w") as fp:
    json.dump({}, fp)

with open(f"end_to_end_tests/fixtures/ckan_publishers/{args.reporting_org_short_name}.json", "w") as fp:
    json.dump(
        {
            "result": {
                "id": uuid.uuid4().hex,
                "name": args.reporting_org_short_name,
                "title": args.reporting_org_human_readable_name,
                "publisher_organization_type": "40",
            }
        },
        fp,
        indent=4,
    )

os.makedirs(f"end_to_end_tests/fixtures/data/{args.reporting_org_short_name}", exist_ok=True)
