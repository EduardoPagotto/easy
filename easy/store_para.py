'''
Created on 20250307
Update on 20250325
@author: Eduardo Pagotto
'''

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional
from tinydb import Storage

from easy.path_mng import PathLocalMng
from easy.sshparamiko import SSHParamiko

logger = logging.getLogger(__name__)

__all__ = ('DumpStorParamiko')

class DumpStorParamiko(Storage):
    def __init__(self, sshfs_url : str, path_mng : Optional[PathLocalMng], cache_size : int):
        """Storage using paramiko

        Args:
            mount_point (str): not used
            conn (str): directory/filename
            sftp_cfg (dict): dictionary with user/host/pass where json file stay
            cache_size (int): size of cached inserts/updates
        """

        self.sshfs_url = sshfs_url
        self.filename = ''
        self.path_remoto = ''
        self.cache_size = cache_size
        self.last_read = 0
        self.tot_read = 0
        self.tot_write = 0

        self.cache = None
        self._cache_modified_count = 0

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
                path_filename = ''
                with SSHParamiko(self.sshfs_url) as remote:

                    path_filename = remote.get_path_filename()
                    logger.info("json opening %s",path_filename)

                    with remote.sftp.open(path_filename, 'r') as handle:

                        handle.prefetch()

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

        logger.warning('flush %s with %d transactions.', self.filename, self._cache_modified_count)

        path_filename = ''
        with SSHParamiko(self.sshfs_url) as sftp:

            path_filename = sftp.get_path_filename()

            self.tot_write += 1
            self.tot_read += self.last_read
            self.cache['_SystemDB'] = {'reads': self.tot_read, 'writes':self.tot_write,'last_save':datetime.now().isoformat()}

            #sftp.get_path(self.path_remoto)

            if sftp.write_json(self.cache, path_filename):
                self.exist_file = True
                self._cache_modified_count = 0

    def close(self):
        """automatic flush in close
        """

        self.flush()
        self.tot_read = 0
        self.tot_write = 0
        self.last_read = 0
        self.cache = None
        self.exist_file = False
