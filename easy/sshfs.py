'''
Created on 20241209
Update on 20250305
@author: Eduardo Pagotto
'''

import logging
import os
import time
from pathlib import Path
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)

__all__ = ('SSHFS', 'umount_point')

def umount_point(mount_point :str) -> bool:
    """umount SSHDFS

    Args:
        mount_point (str): umount point

    Returns:
        bool: True to sucess
    """
    try:
        if os.path.ismount(mount_point):
            os.sync()
            logger.info('execute umount %s', mount_point)
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
    def __init__(self, conn : dict, ro: bool, local : Optional[str] = None):
        """Mount remote SSHFS

        Args:
            conn (dict): data with user/host/pass of sftp server
            ro (bool): True to mount remote sshfs as Read Only
            local (Optional[str], optional): Overrite mount point in conn dictionary. Defaults to None.
        """

        self.conn = conn
        self.ro = ro
        self.local = self.conn['local'] if not local else local

        try:
            # if path nof mount point not exist, create
            if Path(self.local).is_dir():
                umount_point(self.local)
            else:
                # check if mount point already monted if is, dismount(old error connection status)
                logger.info('novo diretorio de montagem: %s', self.local)
                Path(self.local).mkdir(parents=True, exist_ok=True)
        except:
            # any thing wrong Except
            umount_point(self.local)
            raise Exception("Falha SSHFS em %s", self.local)

    def get_local(self) -> str:
        """Get mounted point

        Returns:
            str: path full
        """
        return self.local

    def get_path(self, path : str) -> str:
        """returns the mounted directory plus the parameter, and creates the same if there is no

        Args:
            path (str): directoru used to

        Returns:
            str: joined loca plus path, create directory if not exist
        """

        new_path = os.path.join(self.get_local(), path)
        if os.path.isdir(new_path):
            logger.info('path remoto adquirido: %s', new_path)
            return new_path

        Path(new_path).mkdir(parents=True, exist_ok=True)
        logger.warning('path remoto criado: %s', new_path)
        return new_path


    def __enter__(self):
        """Use as a context manager."""

        try:
            str_ro = '-o ro' if self.ro else '-o rw'

            logger.info("host %s -> %s",str_ro, self.conn['host'])

            cmd = f"echo \'{self.conn['passwd']}\' | sshfs {self.conn['user']}@{self.conn['host']}:{self.conn['remote']} {self.local} -o password_stdin -o allow_other {str_ro}"

            result = subprocess.run(cmd,
                                text=True,
                                shell=True,
                                capture_output=True,
                                executable='/bin/sh')

            if result.returncode != 0:
                raise Exception(f"Falha na montagem: {result.stderr}")

        except Exception as exp:
            raise Exception(str(exp.args))

        return self

    def __exit__(self, *err):
        """Leaving a context."""

        umount_point(self.local)
