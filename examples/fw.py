#!/usr/bin/env python
"""
 This script provides an example of how to connect to an Aviatrix Controller
 and add/delete/etc. firewall policies

 INPUTS:
   $1 - HOST - string - host/ip of the controller
   $2 - USER - string - the username used to authenticate with controller
   $3 - PASSWORD - string - the password of the given USER
   $4 - GW - string - a gateway name to use for testing

"""
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


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

    fw_tag_example(sys.argv[1], sys.argv[2], sys.argv[3])
    fw_policies_example(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

def fw_tag_example(controller_ip, username, password):
    """
    Performs actions related to FW policy tags
    Arguments:
    controller_ip - string - the controller host or IP
    username - string - the controller login username
    password - string - the controller login password
    gw_name - string - name of a gateway
    """

    controller = Aviatrix(controller_ip)
    controller.login(username, password)

    current = controller.list_fw_tags()
    print "1. CURRENT tags: %s" % (current)

    controller.add_fw_tag('TEST_ME')
    current = controller.list_fw_tags()
    if 'TEST_ME' not in current:
        print 'ERROR: TEST_ME tag is missing: %s' % (current)
        return
    print '2. Added TEST_ME tag'

    members = controller.get_fw_tag_members('TEST_ME')
    print '3. current members: %s' % (members)
    members.append({'name': 'fwtag1',
                    'cidr': '192.168.1.0/24'})
    controller.set_fw_tag_members('TEST_ME', members)
    members = controller.get_fw_tag_members('TEST_ME')
    print 'current members: %s' % (members)
    members.append({'name': 'fwtag2',
                    'cidr': '192.168.2.0/24'})
    members.append({'name': 'fwtag3',
                    'cidr': '192.168.3.0/24'})
    members.append({'name': 'fwtag4',
                    'cidr': '192.168.4.0/24'})
    members.append({'name': 'fwtag5',
                    'cidr': '192.168.5.0/24'})
    members.append({'name': 'fwtag6',
                    'cidr': '192.168.6.0/24'})
    controller.set_fw_tag_members('TEST_ME', members)
    members = controller.get_fw_tag_members('TEST_ME')
    print 'current members: %s' % (members)

    controller.set_fw_tag_members('TEST_ME', [])

    controller.delete_fw_tag('TEST_ME')
    current = controller.list_fw_tags()
    if 'TEST_ME' in current:
        print 'ERROR: TEST_ME tag is in %s' % (current)
        return
    print 'Removed TEST_ME tag'

def fw_policies_example(controller_ip, username, password, gw_name):
    """
    Performs actions related to FW policies
    Arguments:
    controller_ip - string - the controller host or IP
    username - string - the controller login username
    password - string - the controller login password
    gw_name - string - name of a gateway to use for testing
    """
    controller = Aviatrix(controller_ip)
    controller.login(username, password)

    gwy = controller.get_gateway_by_name('admin', gw_name)
    if not gwy:
        print 'Gateway %s not found\n' % (gw_name)
        return

    current = controller.get_fw_policy_full('gw-sample-app-dev')
    print 'CURRENT POLICY: %s' % (current)

    rules = current['security_rules']
    rules.append({'protocol': 'all', 's_ip': '192.168.1.0/24',
                  'd_ip': '10.0.0.0/24', 'deny_allow': 'allow', 'port': '',
                  'log_enable': 'off'})
    controller.set_fw_policy_security_rules('gw-sample-app-dev', rules)
    current = controller.get_fw_policy_full('gw-sample-app-dev')
    print 'CURRENT POLICY: %s' % (current)

if __name__ == "__main__":
    main()
