import json
from collections import OrderedDict

from flask import render_template
import config

license_names = {
    'notspecified': 'Other::License Not Specified',
    'odc-pddl': 'OKD Compliant::Open Data Commons Public Domain Dedication and Licence (PDDL)',
    'odc-odbl': 'OKD Compliant::Open Data Commons Open Database License (ODbL)',
    'odc-by': 'OKD Compliant::Open Data Commons Attribution Licence',
    'cc-zero': 'OKD Compliant::Creative Commons CCZero',
    'cc-by': 'OKD Compliant::Creative Commons Attribution',
    'cc-by-sa': 'OKD Compliant::Creative Commons Attribution Share-Alike',
    'gfdl': 'OKD Compliant::GNU Free Documentation License',
    'ukclickusepsi': 'OKD Compliant::UK Click Use PSI',
    'other-open': 'OKD Compliant::Other (Open)',
    'other-pd': 'OKD Compliant::Other (Public Domain)',
    'other-at': 'OKD Compliant::Other (Attribution)',
    'ukcrown-withrights': 'OKD Compliant::UK Crown Copyright with data.gov.uk rights',
    'hesa-withrights': 'OKD Compliant::Higher Education Statistics Agency Copyright with data.gov.uk rights',
    'localauth-withrights': 'OKD Compliant::Local Authority Copyright with data.gov.uk rights',
    'uk-ogl': 'OKD Compliant::UK Open Government Licence (OGL)',
    'met-office-cp': 'Non-OKD Compliant::Met Office UK Climate Projections Licence Agreement',
    'cc-nc': 'Non-OKD Compliant::Creative Commons Non-Commercial (Any)',
    'ukcrown': 'Non-OKD Compliant::UK Crown Copyright',
    'other-nc': 'Non-OKD Compliant::Other (Non-Commercial)',
    'other-closed': 'Non-OKD Compliant::Other (Not Open)',
    'bsd-license': 'OSI Approved::New and Simplified BSD licenses',
    'gpl-2.0': 'OSI Approved::GNU General Public License (GPL)',
    'gpl-3.0': 'OSI Approved::GNU General Public License version 3.0 (GPLv3)',
    'lgpl-2.1': 'OSI Approved::GNU Library or "Lesser" General Public License (LGPL)',
    'mit-license': 'OSI Approved::MIT license',
    'afl-3.0': 'OSI Approved::Academic Free License 3.0 (AFL 3.0)',
    'apl1.0': 'OSI Approved::Adaptive Public License',
    'apache': 'OSI Approved::Apache Software License',
    'apache2.0': 'OSI Approved::Apache License, 2.0',
    'apsl-2.0': 'OSI Approved::Apple Public Source License',
    'artistic-license-2.0': 'OSI Approved::Artistic license 2.0',
    'attribution': 'OSI Approved::Attribution Assurance Licenses',
    'ca-tosl1.1': 'OSI Approved::Computer Associates Trusted Open Source License 1.1',
    'cddl1': 'OSI Approved::Common Development and Distribution License',
    'cpal_1.0': 'OSI Approved::Common Public Attribution License 1.0 (CPAL)',
    'cuaoffice': 'OSI Approved::CUA Office Public License Version 1.0',
    'eudatagrid': 'OSI Approved::EU DataGrid Software License',
    'eclipse-1.0': 'OSI Approved::Eclipse Public License',
    'ecl2': 'OSI Approved::Educational Community License, Version 2.0',
    'eiffel': 'OSI Approved::Eiffel Forum License',
    'ver2_eiffel': 'OSI Approved::Eiffel Forum License V2.0',
    'entessa': 'OSI Approved::Entessa Public License',
    'fair': 'OSI Approved::Fair License',
    'frameworx': 'OSI Approved::Frameworx License',
    'ibmpl': 'OSI Approved::IBM Public License',
    'intel-osl': 'OSI Approved::Intel Open Source License',
    'jabber-osl': 'OSI Approved::Jabber Open Source License',
    'lucent-plan9': 'OSI Approved::Lucent Public License (Plan9)',
    'lucent1.02': 'OSI Approved::Lucent Public License Version 1.02',
    'mitre': 'OSI Approved::MITRE Collaborative Virtual Workspace License (CVW License)',
    'motosoto': 'OSI Approved::Motosoto License',
    'mozilla': 'OSI Approved::Mozilla Public License 1.0 (MPL)',
    'mozilla1.1': 'OSI Approved::Mozilla Public License 1.1 (MPL)',
    'nasa1.3': 'OSI Approved::NASA Open Source Agreement 1.3',
    'naumen': 'OSI Approved::Naumen Public License',
    'nethack': 'OSI Approved::Nethack General Public License',
    'nokia': 'OSI Approved::Nokia Open Source License',
    'oclc2': 'OSI Approved::OCLC Research Public License 2.0',
    'opengroup': 'OSI Approved::Open Group Test Suite License',
    'osl-3.0': 'OSI Approved::Open Software License 3.0 (OSL 3.0)',
    'php': 'OSI Approved::PHP License',
    'pythonpl': 'OSI Approved::Python license',
    'PythonSoftFoundation': 'OSI Approved::Python Software Foundation License',
    'qtpl': 'OSI Approved::Qt Public License (QPL)',
    'real': 'OSI Approved::RealNetworks Public Source License V1.0',
    'rpl1.5': 'OSI Approved::Reciprocal Public License 1.5 (RPL1.5)',
    'ricohpl': 'OSI Approved::Ricoh Source Code Public License',
    'sleepycat': 'OSI Approved::Sleepycat License',
    'sun-issl': 'OSI Approved::Sun Industry Standards Source License (SISSL)',
    'sunpublic': 'OSI Approved::Sun Public License',
    'sybase': 'OSI Approved::Sybase Open Watcom Public License 1.0',
    'UoI-NCSA': 'OSI Approved::University of Illinois/NCSA Open Source License',
    'vovidapl': 'OSI Approved::Vovida Software License v. 1.0',
    'W3C': 'OSI Approved::W3C License',
    'wxwindows': 'OSI Approved::wxWindows Library License',
    'xnet': 'OSI Approved::X.Net License',
    'zpl': 'OSI Approved::Zope Public License',
    'zlib-license': 'OSI Approved::zlib/libpng license'}

with open(config.join_stats_path('licenses.json')) as handler:
    license_urls = json.load(handler)

with open(config.join_stats_path('ckan.json')) as handler:
    ckan = json.load(handler, object_pairs_hook=OrderedDict)

licenses = [
    package['license_id']
    if package['license_id'] is not None
    else 'notspecified'
    for _, publisher in ckan.items()
    for _, package in publisher.items()]


def licenses_for_publisher(publisher_name):
    # Check publisher is in the compiled list of CKAN data
    # Arises from https://github.com/IATI/IATI-Dashboard/issues/408
    if publisher_name not in ckan.keys():
        return set()

    # Return unique licenses used
    return set([
        package['license_id']
        if package['license_id'] is not None
        else 'notspecified'
        for package in ckan[publisher_name].values()])


def main():
    licenses_and_publisher = set([
        (package['license_id']
         if package['license_id'] is not None
         else 'notspecified', publisher_name)
        for publisher_name, publisher in ckan.items()
        for package_name, package in publisher.items()])
    licenses_per_publisher = [license for license, publisher in licenses_and_publisher]
    return render_template('licenses.html',
                           license_names=license_names,
                           license_urls=license_urls,
                           license_count=dict((x, licenses.count(x)) for x in set(licenses)),
                           publisher_license_count=dict((x, licenses_per_publisher.count(x)) for x in set(licenses_per_publisher)),
                           sorted=sorted,
                           page='licenses',
                           licenses=True)


def individual_license(license):
    publishers = [
        publisher_name
        for publisher_name, publisher in ckan.items()
        for _, package in publisher.items()
        if package['license_id'] == license or (
            license == 'notspecified' and package['license_id'] is None)]
    publisher_counts = [(publisher, publishers.count(publisher)) for publisher in set(publishers)]
    return render_template('license.html',
                           license=license,
                           license_names=license_names,
                           license_urls=license_urls,
                           publisher_counts=publisher_counts,
                           page='licenses',
                           licenses=True)
