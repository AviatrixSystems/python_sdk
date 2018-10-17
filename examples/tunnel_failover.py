#!/usr/bin/env python
#-------------------------------------------------------------------------
# This script provides an example of how to connect to an Aviatrix Controller
# and modify configuration of a S2C tunnel when failover from one tunnel to
# another
#
# INPUTS:
#   $1 - HOST - string - host/ip of the controller
#   $2 - USER - string - the username used to authenticate with controller
#   $3 - PASSWORD - string - the password of the given USER
#
#-------------------------------------------------------------------------
from aviatrix import Aviatrix
import logging
import sys

#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

#---------------------------------------------------------------------
# UPDATE THESE
# VPC_ID should match the vpc id in the site2cloud configuration
# CONNECTION_NAME_ACTIVE should match the "active" site2cloud tunnel name
# CONNECTION_NAME_STANDBY should match the "standby" site2cloud tunnel name
# REAL_CIDR should match the real remote CIDR range
# FAKE_CIDR_ACTIVE should be any CIDR to use as a fake CIDR range (one that
#                  does not overlap with anything else on this gateway)
# FAKE_CIDR_STANDBY should be any CIDR to use as a fake CIDR range (one that
#                   does not overlap with anything else on this gateway)
#---------------------------------------------------------------------


VPC_ID = 'vpc-12345678'
CONNECTION_NAME_ACTIVE = 'Tunnel_Name'
CONNECTION_NAME_STANDBY = 'Tunnel_Name_Standby'
REAL_CIDR = '10.0.0.0/16'
FAKE_CIDR_ACTIVE = '100.64.0.0/16'
FAKE_CIDR_STANDBY = '100.64.1.0/16'

if len(sys.argv) != 4:
    print ('usage: %s <HOST> <USER> <PASSWORD>\n'
           '  where\n'
           '    HOST Aviatrix Controller hostname or IP\n'
           '    USER Aviatrix Controller login username\n'
           '    PASSWORD Aviatrix Controller login password\n'
           % sys.argv[0])
    sys.exit(1)

controller_ip = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]

controller = Aviatrix(controller_ip)
controller.login(username, password)

# first, change the active cidr to a fake cidr (so it won't conflict)
controller.set_site2cloud_remote_subnet(VPC_ID, CONNECTION_NAME_ACTIVE, FAKE_CIDR_ACTIVE)

# now the active tunnel and the standby tunnel both have a "fake" CIDR for remote subnet
# next, change the standby to the real CIDR
controller.set_site2cloud_remote_subnet(VPC_ID, CONNECTION_NAME_STANDBY, REAL_CIDR)

