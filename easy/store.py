'''
Created on 20250208
Update on 20250226
@author: Eduardo Pagotto
'''

import json
import logging
import os
from datetime import datetime

from typing import Any, Dict, Optional
from tinydb.storages import Storage

logger = logging.getLogger(__name__)

__all__ = ('DumpStor')

class DumpStor(Storage):
    def __init__(self, filename : str, cache_size : int):

        self.filename = filename
        self.cache_size = cache_size
        self.last_read = 0
        self.tot_read = 0
        self.tot_write = 0

        self.cache = None
        self._cache_modified_count = 0
        self._cache_burst = 0

    def read(self)-> Optional[Dict[str, Dict[str, Any]]]:

        if self.cache:
            return self.cache

        try:
            with open(self.filename, 'r') as handle:
                self.cache =  json.load(handle)

                if '_SystemDB' in self.cache:
                    self.tot_read += 1
                    self.tot_write = self.cache['_SystemDB']['writes']
                    self.last_read = self.cache['_SystemDB']['reads']
                    self.cache.pop('_SystemDB')

                return self.cache

        except json.JSONDecodeError:
            logger.error('malformed db: %s', self.filename)
        except FileNotFoundError:
            pass

        return None


    def write(self, data: Dict[str, Dict[str, Any]]):

        self.cache = data
        self._cache_modified_count += 1

        # Check if we need to flush the cache
        if self._cache_modified_count >= self.cache_size:
            self._cache_burst += 1
            logger.warning('cache burst: %d', self._cache_burst)
            self.flush()

    def flush(self):

        if self._cache_modified_count == 0:
            return

        self._cache_modified_count = 0

        self.tot_write += 1
        self.tot_read += self.last_read
        self.cache['_SystemDB'] = {'reads': self.tot_read, 'writes':self.tot_write,'last_save':datetime.now().isoformat()}

        json_object = json.dumps(self.cache, ensure_ascii=False)

        if os.path.isfile(self.filename):
            os.unlink(self.filename)

        with open(self.filename, "w") as outfile:
            outfile.write(json_object)

    def close(self):
        self.flush()
        self.tot_read = 0
        self.tot_write = 0
        self.last_read = 0
        self.cache = None
        self._cache_burst = 0
