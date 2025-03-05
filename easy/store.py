'''
Created on 20250208
Update on 20250305
@author: Eduardo Pagotto
'''

import json
import logging
import os
from datetime import datetime

from typing import Any, Dict, Optional
from tinydb.storages import Storage

from easy.sshfs import SSHFS

logger = logging.getLogger(__name__)

__all__ = ('DumpStor', 'DumpStorSSH')

class DumpStor(Storage):
    def __init__(self, filename : str, cache_size : int):
        """Create/acess a json data file

        Args:
            filename (str): path file name of json file
            cache_size (int): number of insert or update until automatic flush do file
        """

        self.filename = filename
        self.cache_size = cache_size
        self.last_read = 0
        self.tot_read = 0
        self.tot_write = 0

        self.cache = None
        self._cache_modified_count = 0
        self._cache_burst = 0

        self.exist_file = True

    def read(self)-> Optional[Dict[str, Dict[str, Any]]]:
        """Read entry used to get data in file

        Returns:
            Optional[Dict[str, Dict[str, Any]]]: dataof json in dictionary
        """

        if self.cache:
            return self.cache

        if self.exist_file:

            try:
                logger.info("json opening %s", self.filename)
                with open(self.filename, 'r') as handle:
                    self.cache =  json.load(handle)

                    if '_SystemDB' in self.cache:
                        self.tot_read += 1
                        self.tot_write = self.cache['_SystemDB']['writes']
                        self.last_read = self.cache['_SystemDB']['reads']
                        self.cache.pop('_SystemDB')

                    return self.cache

            except json.JSONDecodeError:
                logger.error('json %s malformed', self.filename)
            except FileNotFoundError:
                logger.warning('json %s not exist', self.filename)

        self.exist_file = False
        return None

    def write(self, data: Dict[str, Dict[str, Any]]):
        """Write dictionary to file json

        Args:
            data (Dict[str, Dict[str, Any]]): data to save
        """

        self.cache = data
        self._cache_modified_count += 1

        # Check if we need to flush the cache
        if self._cache_modified_count >= self.cache_size:
            self.flush()

    def flush(self):
        """execute a write pendents
        """

        if self._cache_modified_count == 0:
            return

        self._cache_burst += 1
        logger.warning('flush in %d transactions.', self._cache_burst)

        self._cache_modified_count = 0

        self.tot_write += 1
        self.tot_read += self.last_read
        self.cache['_SystemDB'] = {'reads': self.tot_read, 'writes':self.tot_write,'last_save':datetime.now().isoformat()}

        json_object = json.dumps(self.cache, ensure_ascii=False)

        if os.path.isfile(self.filename):
            os.unlink(self.filename)
        else:
            logger.warning('json %s will be create',self.filename)
            self.exist_file = True

        with open(self.filename, "w") as outfile:
            outfile.write(json_object)

    def close(self):
        """automatic flush in close
        """

        self.flush()
        self.tot_read = 0
        self.tot_write = 0
        self.last_read = 0
        self.cache = None
        self._cache_burst = 0
        self.exist_file = False


class DumpStorSSH(Storage):
    def __init__(self, mount_point : str, conn : str, sftp_cfg : dict, cache_size : int):
        """_sumCreate a temporary conection to access remote json data filemary_

        Args:
            mount_point (str): loacal mount point used to create/use directory structure of json file
            conn (str): directory/file used to json file
            sftp_cfg (dict): dictionary with user/host/pass where json file stay
            cache_size (int): number of insert or update until automatic flush do file.
        """

        self.mount_point = mount_point
        self.conn = conn
        self.filename = ''
        self.sftp_cfg = sftp_cfg
        self.cache_size = cache_size
        self.last_read = 0
        self.tot_read = 0
        self.tot_write = 0

        self.cache = None
        self._cache_modified_count = 0
        self._cache_burst = 0

        self.exist_file = True

    def read(self)-> Optional[Dict[str, Dict[str, Any]]]:
        """Read entry used to get data in file

        Returns:
            Optional[Dict[str, Dict[str, Any]]]: dataof json in dictionary
        """

        if self.cache:
            return self.cache

        if self.exist_file:

            try:

                with SSHFS(self.sftp_cfg, False, self.mount_point) as remote:

                    p, f = os.path.split(self.conn)
                    path_remoto : str = remote.get_path(p)
                    self.filename = os.path.join(path_remoto, f + u".json")

                    logger.info("json opening %s", self.filename)
                    with open(self.filename, 'r') as handle:
                        self.cache =  json.load(handle)

                        if '_SystemDB' in self.cache:
                            self.tot_read += 1
                            self.tot_write = self.cache['_SystemDB']['writes']
                            self.last_read = self.cache['_SystemDB']['reads']
                            self.cache.pop('_SystemDB')

                        return self.cache

            except json.JSONDecodeError:
                logger.error('json %s malformed', self.filename)
            except FileNotFoundError:
                logger.warning('json %s not exist', self.filename)

        self.exist_file = False
        return None


    def write(self, data: Dict[str, Dict[str, Any]]):
        """Write dictionary to file json

        Args:
            data (Dict[str, Dict[str, Any]]): data to save
        """

        self.cache = data
        self._cache_modified_count += 1

        # Check if we need to flush the cache
        if self._cache_modified_count >= self.cache_size:
            self.flush()

    def flush(self):
        """execute a write pendents
        """

        if self._cache_modified_count == 0:
            return

        self._cache_burst += 1
        logger.warning('flush in %d transactions.', self._cache_burst)

        with SSHFS(self.sftp_cfg, False, self.mount_point) as remote:

            self._cache_modified_count = 0

            self.tot_write += 1
            self.tot_read += self.last_read
            self.cache['_SystemDB'] = {'reads': self.tot_read, 'writes':self.tot_write,'last_save':datetime.now().isoformat()}

            json_object = json.dumps(self.cache, ensure_ascii=False)

            if os.path.isfile(self.filename):
                os.unlink(self.filename)
            else:
                logger.warning('json %s will be create',self.filename)
                self.exist_file = True

            with open(self.filename, "w") as outfile:
                outfile.write(json_object)

    def close(self):
        """automatic flush in close
        """

        self.flush()
        self.tot_read = 0
        self.tot_write = 0
        self.last_read = 0
        self.cache = None
        self._cache_burst = 0
        self.exist_file = False
