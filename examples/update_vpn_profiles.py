#!/usr/bin/env python

"""
# This script provides an example of how to connect to an Aviatrix Controller
# and update user vpn profiles
#
# INPUTS:
#   $1 - HOST - string - host/ip of the controller
#   $2 - USER - string - the username used to authenticate with controller
#   $3 - PASSWORD - string - the password of the given USER
#
"""

import logging
import sys

from aviatrix import Aviatrix

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def main():
    """
    main() interface to this script
    """
    if len(sys.argv) != 4:
        print ('usage: %s <HOST> <USER> <PASSWORD>\n'
               '  where\n'
               '    HOST Aviatrix Controller hostname or IP\n'
               '    USER Aviatrix Controller login username\n'
               '    PASSWORD Aviatrix Controller login password\n' % sys.argv[0])
        sys.exit(1)

    # connect to the controller
    controller_ip = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    controller = Aviatrix(controller_ip)
    controller.login(username, password)

    create_profiles(controller)
    attach_users(controller)
    detach_users(controller)
    cleanup_profiles(controller)

def create_profiles(controller):
    """
    Creates the profiles required
    Arguments:
    controller - reference to Aviatrix Controller
    """

    current = controller.list_vpn_profiles()
    print 'CURRENT: %s' % (current)

    if 'TEST1' not in current.keys():
        controller.add_vpn_profile('TEST1')
    current = controller.list_vpn_profile_policies('TEST1')
    print 'POLICIES: %s' % (current)
    policies = [
        {'action': 'allow', 'protocol': 'all', 'target': '10.0.0.0/24', 'port': '0:1024'},
        {'action': 'allow', 'protocol': 'tcp', 'target': '192.168.0.0/24', 'port': '22'},
        {'action': 'deny', 'protocol': 'all', 'target': '172.16.0.0/24', 'port': '0:1024'}
    ]
    controller.update_vpn_profile_policies('TEST1', policies)
    current = controller.list_vpn_profile_policies('TEST1')
    print 'POLICIES: %s' % (current)
    controller.add_vpn_profile('TEST2', 'allow_all')
    controller.add_vpn_profile('TEST3', 'deny_all')

    current = controller.list_vpn_profiles()
    print 'AFTER: %s' % (current)

def attach_users(controller):
    """
    Attach users to profiles
    """

    controller.add_vpn_profile_member('TEST1', 'test2')
    controller.add_vpn_profile_member('TEST2', 'test3')
    controller.add_vpn_profile_member('TEST3', 'test3')

def detach_users(controller):
    """
    Detachs users created with attach_users
    """
    controller.delete_vpn_profile_member('TEST1', 'test2')
    controller.delete_vpn_profile_member('TEST2', 'test3')
    controller.delete_vpn_profile_member('TEST3', 'test3')

def cleanup_profiles(controller):
    """
    Cleans up the profiles created by create_profiles()
    Arguments:
    controller - reference to the Aviatrix Controller
    """

    controller.delete_vpn_profile('TEST1')
    controller.delete_vpn_profile('TEST2')
    controller.delete_vpn_profile('TEST3')

if __name__ == "__main__":
    main()
