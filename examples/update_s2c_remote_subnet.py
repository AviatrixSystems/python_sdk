#!/usr/bin/env python
#-------------------------------------------------------------------------
# This script provides an example of how to connect to an Aviatrix Controller
# and update a S2C tunnel's remote subnet configuration
#
# INPUTS:
#   $1 - HOST - string - host/ip of the controller
#   $2 - USER - string - the username used to authenticate with controller
#   $3 - PASSWORD - string - the password of the given USER
#   $4 - VPC_ID - string - VPC Id
#   $5 - CONN_NAME - string - connection name
#   $6 - NEW_SUBNET - string - new CIDR
#
#-------------------------------------------------------------------------
from aviatrix import Aviatrix
import logging
import sys

if len(sys.argv) != 7:
    print ('usage: %s <HOST> <USER> <PASSWORD> <VPC_ID> <CONN_NAME> <NEW_SUBNET>\n'
           '  where\n'
           '    HOST Aviatrix Controller hostname or IP\n'
           '    USER Aviatrix Controller login username\n'
           '    PASSWORD Aviatrix Controller login password\n'
           '    VPC_ID the VPC ID\n'
           '    CONN_NAME the s2c connection name\n'
           '    NEW_SUBNET the new CIDR for remote side\n' % sys.argv[0])
    sys.exit(1)

controller_ip = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]
vpc_id = sys.argv[4]
conn_name = sys.argv[5]
new_subnet = sys.argv[6]
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

controller = Aviatrix(controller_ip)
controller.login(username, password)
controller.set_site2cloud_remote_subnet(vpc_id, conn_name, new_subnet)
