#!/usr/bin/env python
"""
 This script provides an example of how to connect to an Aviatrix Controller
 and add/delete/etc. FQDN filters on a gateway.

 INPUTS:
   $1 - HOST - string - host/ip of the controller
   $2 - USER - string - the username used to authenticate with controller
   $3 - PASSWORD - string - the password of the given USER
   $4 - GW - string - a gateway name to use

"""
#import logging
import sys
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

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
               '    GW name of a provisioned gateway\n' % sys.argv[0])
        sys.exit(1)

    fqdn_example(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

def fqdn_example(controller_ip, username, password, gw_name):
    """
    Performs actions related to FQDN filters
    Arguments:
    controller_ip - string - the controller host or IP
    username - string - the controller login username
    password - string - the controller login password
    gw_name - string - name of a gateway
    """
    controller = Aviatrix(controller_ip)
    controller.login(username, password)

    gwy = controller.get_gateway_by_name('admin', gw_name)
    if not gwy:
        print 'Gateway %s not found\n' % (gw_name)
        return

    controller.enable_snat(gw_name)
    controller.add_fqdn_filter_tag('TEST_TAG')
    tags = controller.list_fqdn_filters()
    if 'TEST_TAG' not in tags:
        print 'TEST_TAG not found!\n'
        return

    controller.delete_fqdn_filter_tag('TEST_TAG')
    tags = controller.list_fqdn_filters()
    if 'TEST_TAG' in tags:
        print 'TEST_TAG found!\n'
        return
    controller.add_fqdn_filter_tag('TEST_TAG')
    try:
        controller.set_fqdn_filter_domain_list('TEST_TAG', ['*.google.com', 'cnn.com', '*.aviatrix.com'])
    except BaseException, e:
        print str(e)
        pass

    print 'TEST_TAG:%s' % (controller.get_fqdn_filter_domain_list('TEST_TAG'))

    controller.attach_fqdn_filter_to_gateway('TEST_TAG', gw_name)
    gws = controller.list_fqdn_filter_gateways('TEST_TAG')
    if gw_name not in gws:
        print '%s not found attached to TEST_TAG!\n' % (gw_name)
        return

    controller.detach_fqdn_filter_from_gateway('TEST_TAG', gw_name)
    gws = controller.list_fqdn_filter_gateways('TEST_TAG')
    if gw_name in gws:
        print '%s found attached to TEST_TAG!\n' % (gw_name)
        return

    controller.enable_fqdn_filter('TEST_TAG')
    controller.disable_fqdn_filter('TEST_TAG')
    controller.enable_fqdn_filter('TEST_TAG')
    controller.delete_fqdn_filter_tag('TEST_TAG')
    controller.disable_snat(gw_name)

if __name__ == "__main__":
    main()
