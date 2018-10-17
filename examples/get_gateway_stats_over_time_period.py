#!/usr/bin/env python
"""
 This script provides an example of how to connect to an Aviatrix Controller
 and get the statistics of a gateway over specific time period

 INPUTS:
   $1 - HOST - string - host/ip of the controller
   $2 - USER - string - the username used to authenticate with controller
   $3 - PASSWORD - string - the password of the given USER
   $4 - GW - string the gateway name to retrieve diagnostics for
"""
#import logging
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
from datetime import datetime, timedelta
import json
import sys

from aviatrix import Aviatrix

def main():
    """
    main() interface to this script
    """
    if len(sys.argv) != 5:
        print ('usage: %s <HOST> <USER> <PASSWORD> <GW>\n'
               '  where\n'
               '    HOST Aviatrix Controller hostname or IP\n'
               '    USER Aviatrix Controller login username\n'
               '    PASSWORD Aviatrix Controller login password\n'
               '    GW Aviatrix gateway name\n' % sys.argv[0])
        sys.exit(1)

    get_stats(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

def get_stats(controller_ip, username, password, gwy_name):
    """
    Prints the statistics to stdout
    Arguments:
    controller_ip - string - the controller host or IP
    username - string - the controller login username
    password - string - the controller login password
    gwy_name - string - the gateway name
    """
    controller = Aviatrix(controller_ip)
    controller.login(username, password)

    print 'Getting stats for gateway %s ...' % (gwy_name)
    end = datetime.now()
    start = end - timedelta(days=1)
    stats = controller.get_gateway_statistic_over_time(
        gwy_name, start, end, Aviatrix.StatName.DATA_AVG_TOTAL)
    print '%s' % (json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()
