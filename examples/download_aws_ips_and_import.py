"""
This script downloads the latest AWS ip-ranges.json file and imports
the list into Aviatrix Controller Firewall tag called 'Amazon IP Address Ranges'

INPUT:
  $1 - SRC_USER::SRC_PASSWD@@SRC_HOST - string - host/ip and login details of the source controller
"""

import json
#import logging
import sys
import urllib

from aviatrix import Aviatrix
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
AVX_TAG_NAME = 'Amazon IP Address Ranges'
AWS_IP_RANGES_DOWNLOAD_URL = 'https://ip-ranges.amazonaws.com/ip-ranges.json'
AWS_REGIONS = ['us-west-1', 'us-east-2']

def download_latest_from_aws():
    """
    Downloads the ip-ranges.json file from AWS and returns a dictionary
    parsed from the JSON object returned.
    """
    response = urllib.urlopen(AWS_IP_RANGES_DOWNLOAD_URL)
    return json.loads(response.read())

def build_aviatrix_formatted_data(ipranges):
    """
    Takes the ip-ranges.json data and reformats it into an array of objects:
    {"cidr": "<<prefix>>", "name": "AWS"}
    """

    if 'prefixes' not in ipranges:
        raise ValueError('ip-ranges.json file not formatted as expected')

    rtn = []

    for prefix in ipranges['prefixes']:
        if prefix['region'] not in AWS_REGIONS:
            continue
        if len(rtn) > 473:
            return rtn
        rtn.append({'cidr': prefix['ip_prefix'],
                    'name': 'AWS'})
    return rtn

def get_controller_from_argument(arg):
    """
    Gets an Aviatrix Controller object from a string of the format:
         USER::PASSWD@@HOST
    """

    userpw, controller_host = arg.split('@@')
    username, password = userpw.split('::')

    controller = Aviatrix(controller_host)
    controller.login(username, password)
    return controller

def main():
    """
    Main interface to this script
    """

    if len(sys.argv) != 2:
        print 'usage: %s <CONTROLLER_USER::CONTROLLER_PASSWD@@CONTROLLER_HOST>\n' % sys.argv[0]
        sys.exit(1)

    # connect to AVX controller
    controller = get_controller_from_argument(sys.argv[1])

    # generate list of CIDRs
    new_members = build_aviatrix_formatted_data(download_latest_from_aws())

    # update the list
    controller.set_fw_tag_members(AVX_TAG_NAME, new_members)

if __name__ == '__main__':
    main()
