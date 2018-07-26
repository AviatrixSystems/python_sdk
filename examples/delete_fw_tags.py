#!/usr/bin/env python
"""
 This script provides an example of how to connect to an Aviatrix Controller
 and delete the stateful firewal tags.

 INPUTS:
   $1 - SRC_USER::SRC_PASSWD@@SRC_HOST - string - host/ip and login details of the source controller

"""
import logging
import sys

from aviatrix import Aviatrix

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
DELETE_TAGS = ['Amazon IP Address Ranges']

def main():
    """
    main() interface to this script
    """
    if len(sys.argv) != 2:
        print 'usage: %s <USER::PASSWD@@HOST>\n' % sys.argv[0]
        sys.exit(1)

    # connect to controller
    controller = get_controller_from_argument(sys.argv[1])

    # delete tags
    fw_tags = controller.list_fw_tags()
    for tag in fw_tags:
        if tag in DELETE_TAGS:
            logging.info('Deleting tag %s ...', tag)
            controller.set_fw_tag_members(tag, [])
            controller.delete_fw_tag(tag)

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

if __name__ == "__main__":
    main()
