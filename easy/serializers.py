'''
Created on 20250208
Update on 20250210
@author: Eduardo Pagotto
'''

from datetime import datetime
from tinydb_serialization import Serializer

class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime

    def __init__(self, dateformat='%Y-%m-%dT%H:%M:%S', *args, **kwargs):
        # super(DateTimeSerializer, self).__init__(*args, **kwargs)
        self._format = dateformat

    def encode(self, obj):
        return obj.strftime(self._format)

    def decode(self, s):
        return self.OBJ_CLASS.strptime(s, self._format)
