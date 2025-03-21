'''
Created on 20250320
Update on 20250320
@author: Eduardo Pagotto
'''

# ref: https://stackoverflow.com/questions/4360050/circularly-linked-list-in-python

import logging
from typing import Optional, Self

logger = logging.getLogger(__name__)


# class MountData():
#     __slots__ = ('mount_point','reserved')
#     def __init__(self, mount : str):
#         self.mount_point = mount
#         self.reserved : bool = False

#     def __str__(self):
#         return f'{self.mount_point}:{self.reserved}'


class MountNode:

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

def build_linkedList(tot : int) -> MountNode:

    root : MountNode = None
    for idx in range(0, tot):
        if not root:
            root = MountNode(f'/mnt/remote{idx}', None)
            root.next = root
        else:
            cursor = root
            while cursor.next != root:
                cursor = cursor.next

            cursor.next = MountNode(f'/mnt/remote{idx}', root)

    return root
