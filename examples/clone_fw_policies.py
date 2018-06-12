#!/usr/bin/env python
"""
 This script provides an example of how to connect to 2 Aviatrix Controllers
 and copy the firewall configuration from one to the other.

 INPUTS:
   $1 - SRC_USER::SRC_PASSWD@@SRC_HOST - string - host/ip and login details of the source controller
   $2 - DST_USER::DST_PASSWD@@DST_HOST - string - host/ip and login details of the destination controller
   $3 - SRC_GW - string - source gateway name to use
   $3 - DST_GW - string - destination gateway name to use

"""
import logging
import sys

from aviatrix import Aviatrix

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def main():
    """
    main() interface to this script
    """
    if len(sys.argv) != 5:
        print ('usage: %s <SRC_USER::SRC_PASSWD@@SRC_HOST> '
               '<DEST_USER:DEST_PASSWD@DEST_HOST> SRC_GW DEST_GW\n'
               '  where\n'
               '    HOST Aviatrix Controller hostname or IP\n'
               '    USER Aviatrix Controller login username\n'
               '    PASSWORD Aviatrix Controller login password\n'
               '    GW name of a provisioned gateway\n' % sys.argv[0])
        sys.exit(1)

    # connect to both controllers
    src_controller = get_controller_from_argument(sys.argv[1])
    dst_controller = get_controller_from_argument(sys.argv[2])

    # find the source gateway
    gw_name = sys.argv[3]
    src_gwy = src_controller.get_gateway_by_name('admin', gw_name)
    if not src_gwy:
        print 'Source gateway %s not found\n' % (gw_name)
        return

    # find the destination gateway
    gw_name = sys.argv[4]
    dst_gwy = src_controller.get_gateway_by_name('admin', gw_name)
    if not dst_gwy:
        print 'Destination gateway %s not found\n' % (gw_name)
        return

    # clone the firewall policies and the FQDN filters
    clone_fw_rules(src_controller, src_gwy, dst_controller, dst_gwy)
    clone_fqdn_rules(src_controller, src_gwy, dst_controller, dst_gwy)

def get_controller_from_argument(arg):
    """
    Gets an Aviatrix Controller object from a string of the format:
         USER::PASSWD@@HOST
    """

    userpw, controller_host = arg.split('@@')
    username, password = userpw.split('::')

    logging.debug('Connecting to Aviatrix @ %s', controller_host)
    controller = Aviatrix(controller_host)
    controller.login(username, password)
    return controller

def clone_fw_rules(src_controller, src_gwy,
                   dst_controller, dst_gwy):
    """
    Clone the firewall rules associated with the given gateway
    Arguments:
    src_controller - Aviatrix object - aviatrix controller (source)
    src_gwy - Dictionary(aviatrix gateway) - aviatrix gateway object (source)
    dst_controller - Aviatrix object - aviatrix controller (destination)
    dst_gwy - Dictionary(aviatrix gateway) - aviatrix gateway obj (destination)
    """

    # STEP 1: clone fw tags
    src_fw_tags = src_controller.list_fw_tags()
    dst_fw_tags = dst_controller.list_fw_tags()
    for tag in src_fw_tags:
        if tag not in dst_fw_tags:
            logging.info('Adding tag %s ...', tag)
            dst_controller.add_fw_tag(tag)
            members = src_controller.get_fw_tag_members(tag)
            dst_controller.set_fw_tag_members(tag, members)
        else:
            logging.warn('FW tag \'%s\' already present in destination', tag)
            # NOTE: it may be appropriate to match the members from the source
            # with this destination so they match

    # STEP 2: clone fw rules on gateway
    src_policy = src_controller.get_fw_policy_full(src_gwy['vpc_name'])
    dst_policy = dst_controller.get_fw_policy_full(dst_gwy['vpc_name'])

    # base policy
    # this is written to only update base_policy OR base_policy_log_enable
    # due to a bug in the Aviatrix API.  Only one of these may be set at a time.
    # So, we get the dest current value and compare with src value and update
    # one of the values at once (if both changed)
    if dst_policy['base_policy'] != src_policy['base_policy']:
        logging.info('Updating firewall base policy to %s', src_policy['base_policy'])
        dst_controller.set_fw_policy_base(dst_gwy['vpc_name'],
                                          src_policy['base_policy'],
                                          dst_policy['base_policy_log_enable'])
        dst_policy = dst_controller.get_fw_policy_full(dst_gwy['vpc_name'])

    if dst_policy['base_policy_log_enable'] != src_policy['base_policy_log_enable']:
        logging.info('Updating firewall base log policy to %s',
                     src_policy['base_policy_log_enable'])
        dst_controller.set_fw_policy_base(dst_gwy['vpc_name'],
                                          dst_policy['base_policy'],
                                          src_policy['base_policy_log_enable'])

    # set the rules
    logging.info('Setting firewall rules ...')
    dst_controller.set_fw_policy_security_rules(dst_gwy['vpc_name'],
                                                src_policy['security_rules'])

def clone_fqdn_rules(src_controller, src_gwy,
                     dst_controller, dst_gwy):
    """
    Clone the firewall FQDN rules associated with the given gateway
    Arguments:
    src_controller - Aviatrix object - aviatrix controller (source)
    src_gwy - Dictionary(aviatrix gateway) - aviatrix gateway object (source)
    dst_controller - Aviatrix object - aviatrix controller (destination)
    dst_gwy - Dictionary(aviatrix gateway) - aviatrix gateway obj (destination)
    """

    # make sure NAT is enabled
    if dst_gwy['enable_nat'] != 'yes':
        logging.info('Enabling NAT ...')
        dst_controller.enable_nat(dst_gwy['vpc_name'])

    # FQDN filters
    src_tags = src_controller.list_fqdn_filters()
    dst_tags = dst_controller.list_fqdn_filters()
    for tag in src_tags.keys():
        if tag not in dst_tags.keys():
            src_tag_details = src_tags[tag]
            logging.info('Adding FQDN filter tag %s ...', tag)
            dst_controller.add_fqdn_filter_tag(tag)
            domains = src_controller.get_fqdn_filter_domain_list(tag)
            dst_controller.set_fqdn_filter_domain_list(tag, domains)
            if src_tag_details['state'] == 'enabled':
                dst_controller.enable_fqdn_filter(tag)
            # NOTE: it may be appropriate to attach the gateway to the tags
            # here also
        else:
            logging.warn('FQDN Filter Tag %s already present in destination', tag)
            # NOTE: it may be appropriate to update the domains associated
            # with this filter so it matches the source

if __name__ == "__main__":
    main()
