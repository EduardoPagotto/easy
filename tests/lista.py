#!/usr/bin/env python3
'''
Created on 20250320
Update on 20250325
@author: Eduardo Pagotto
'''


import logging
import sys
sys.path.append('.')

from easy.path_mng import PathLocalMng

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s')

logger = logging.getLogger('lista')

if __name__ == "__main__":

    path_mng = PathLocalMng(4)

    node0 = path_mng.reserv()
    logger.info(str(node0.get_path()))

    node1 = path_mng.reserv()
    logger.info(str(node1.get_path()))

    node2 = path_mng.reserv()
    logger.info(str(node2.get_path()))

    node3 = path_mng.reserv()
    logger.info(str(node3.get_path()))

    node2.reselase()

    node4 = path_mng.reserv()
    logger.info(str(node4.get_path()))

    node0.reselase()

    node5 = path_mng.reserv()
    logger.info(str(node5.get_path()))

    logger.info(str(path_mng))

    path_mng.release_all()
