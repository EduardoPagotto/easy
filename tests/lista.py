#!/usr/bin/env python3
'''
Created on 20250320
Update on 20250320
@author: Eduardo Pagotto
'''


import logging
import sys
sys.path.append('.')

from easy.mount_node import build_linkedList

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s')

logger = logging.getLogger('lista')

if __name__ == "__main__":

    root = build_linkedList(3)

    node0 = root.reserv()
    logger.info(str(node0.get_data()))

    node1 = root.reserv()
    logger.info(str(node1.get_data()))

    node2 = root.reserv()
    logger.info(str(node2.get_data()))

    node2.reselase()

    node3 = root.reserv()
    logger.info(str(node3.get_data()))

    node0.reselase()

    node4 = root.reserv()
    logger.info(str(node4.get_data()))
