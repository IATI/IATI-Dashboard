import re


def firstint(s):
    if s[0].startswith("<"):
        return 0
    m = re.search(r"\d+", s[0])
    return int(m.group(0))


def get_codelist_values(codelist_values_for_element):
    """Return a list of unique values present within a one-level nested dictionary.
    Envisaged usage is to gather the codelist values used by each publisher, as in
    stats/current/inverted-publisher/codelist_values_by_major_version.json
    Input: Set of codelist values for a given element (listed by publisher), for example:
           current_stats['inverted_publisher']['codelist_values_by_major_version']['1']['.//@xml:lang']
    """
    return list(set([y for x in codelist_values_for_element.items() for y in list(x[1].keys())]))
