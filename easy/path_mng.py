'''
Created on 20250320
Update on 20250320
@author: Eduardo Pagotto
'''

import logging
from typing import Optional, Self

logger = logging.getLogger(__name__)

class PathNode:

    __slots__ = ('mount_point', 'reserved', 'next')

    def __init__(self, mount_point : str, parent : Optional[Self]):
        self.mount_point : str = mount_point
        self.reserved : bool = False
        self.next  : Optional[Self] = parent

    def __str__(self):

        list_link = []

        list_link.append(f'{self.mount_point}:{self.reserved}')
        node = self.next

        while node != self:
            list_link.append(f'{node.mount_point}:{node.reserved}')
            node = node.next

        return str(list_link)


    def reserv(self, start : Optional[Self] = None) -> Self:
        if not self.reserved:
            self.reserved = True
            return self

        if start == None:
            return self.next.reserv(self)

        if start == self:
            return None

        return self.next.reserv(start)

    def reselase(self) -> None:
        self.reserved = False

    def get_data(self) -> str:
        return self.mount_point

class PathLocalMng:
    def __init__(self, tot : int):

        if tot < 3:
            tot = 3

        root : PathNode = None
        for idx in range(0, tot):
            if not root:
                root = PathNode(f'/mnt/remote{idx}', None)
                root.next = root
            else:
                cursor = root
                while cursor.next != root:
                    cursor = cursor.next

                cursor.next = PathNode(f'/mnt/remote{idx}', root)

        self.root : PathNode = root

    def __str__(self):
        return str(self.root)

    def reserv(self) -> PathNode:
        return self.root.reserv()

    def release_all(self):

        lst_tmp = []
        prox = self.root
        while  True:
            lst_tmp.append(prox)
            prox = prox.next
            if prox == self.root:
                break

        for item in lst_tmp:
            item.next = None
            item = None

        del lst_tmp
        del self.root
