'''
Created on 20241209
Update on 20250326
@author: Eduardo Pagotto
'''

import json
import logging
import os
import time
from pathlib import Path
import subprocess
from urllib.parse import urlparse, urlsplit, parse_qsl

from easy.path_mng import PathLocalMng

logger = logging.getLogger(__name__)

__all__ = ('SSHFS', 'umount_point')

def umount_point(mount_point :str, force : bool = False) -> bool:
    """umount SSHDFS

    Args:
        mount_point (str): umount point

    Returns:
        bool: True to sucess
    """
    try:
        if not force:
            if os.path.ismount(mount_point):
                os.sync()
                #logger.info('execute umount %s', mount_point)
                time.sleep(0.5)
            else:
                return True

        result = subprocess.run(f"umount {mount_point}",
                                text=True,
                                shell=True,
                                capture_output=True,
                                executable='/bin/sh')

        if result.returncode != 0:
            logger.warning('execute umount falhou: %s', result.stderr.replace('\n',''))
        else:
            return True

    except Exception as exp:
        logger.error("umount falhou %s", str(exp.args))

    return False

class SSHFS(object):
    def __init__(self, sshfs_url : str, ro: bool, path_mng : PathLocalMng):
        """Mount remote SSHFS
        Args:
            sshfs_url (str): sftp url
            ro (bool): True to mount remote sshfs as Read Only
            path_mng PathLocalMng: path manager to get a valid free local path to mount
        """

        p = urlparse(sshfs_url)
        if p.scheme != 'sftp':
            raise Exception('URI wrong schemma')

        self.params = dict(parse_qsl(urlsplit(sshfs_url).query))

        self.user = p.username
        self.password = p.password
        self.host = p.hostname
        self.remote, f = os.path.split(p.path)
        self.path_node = path_mng.reserv()
        self.filename = os.path.join(self.path_node.get_path(), f) if f else ''

        self.ro = ro

        local = self.get_local()
        try:
            # if path nof mount point not exist, create
            if Path(local).is_dir():
                umount_point(local)
            else:
                # check if mount point already monted if is, dismount(old error connection status)
                logger.info('novo diretorio de montagem: %s', local)
                Path(local).mkdir(parents=True, exist_ok=True)
        except Exception as exp:
            # any thing wrong Except
            umount_point(local, True)
            raise Exception("Falha %s, SSHFS em %s", str(exp.args), self.local)

    def get_local(self) -> str:
        """Get mounted point

        Returns:
            str: path full
        """
        return self.path_node.get_path()

    def get_path_filename(self) -> str:
        return self.filename

    def get_path(self, path : str) -> str:
        """returns the mounted directory plus the parameter, and creates the same if there is no

        Args:
            path (str): directoru used to

        Returns:
            str: joined loca plus path, create directory if not exist
        """

        new_path = os.path.join(self.get_local(), path)
        if os.path.isdir(new_path):
            #logger.info('path remoto adquirido: %s', new_path)
            return new_path

        Path(new_path).mkdir(parents=True, exist_ok=True)
        logger.warning('remote path create: %s', new_path)
        return new_path


    def __enter__(self):
        """Use as a context manager."""

        try:
            str_ro = '-o ro' if self.ro else '-o rw'

            cmd = f"echo \'{self.password}\' | sshfs {self.user}@{self.host}:{self.remote} {self.get_local()} -o password_stdin -o allow_other {str_ro}"

            result = subprocess.run(cmd,
                                text=True,
                                shell=True,
                                capture_output=True,
                                executable='/bin/sh')

            if result.returncode != 0:
                raise Exception(f"Falha na montagem: {result.stderr}")

        except Exception as exp:
            raise Exception(str(exp.args))

        loc = self.get_local()
        if 'dir' in self.params:
            new_path = self.params['dir']
            if len(new_path) > 0:
                loc = self.get_path(new_path)

        if 'file' in self.params:
            filename = self.params['file']
            if len(filename) > 0:
                self.filename = os.path.join(loc, filename)

        return self

    def __exit__(self, *err):
        """Leaving a context."""

        umount_point(self.get_local())
        self.path_node.reselase()


    def write_json_url(self, rec : dict) -> bool:
        return self.write_json(rec, self.filename)


    def write_json(self, recordset : dict, file_name : str) -> bool:

        try:
            json_object = json.dumps(recordset, ensure_ascii=False)

            if os.path.isfile(file_name):
                os.unlink(file_name)

            with open(file_name, "w") as outfile:
                outfile.write(json_object)
                return True

        except (Exception) as exp:
            logger.error("Fail write file %s -> %s", file_name, str(exp.args))

        return False

    def list_files(self, pathfile : str) -> list[str]:
        pathlocal : str = self.get_path(pathfile)
        return sorted(os.listdir(pathlocal))
