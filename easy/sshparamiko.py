'''
Created on 20250307
Update on 20250307
@author: Eduardo Pagotto
'''

import json
import logging
import paramiko

logger = logging.getLogger(__name__)

__all__ = ('SSHParamiko')

class SSHParamiko(object):
    def __init__(self, sftp_cfg : dict):
        """Open sftp session

        Args:
            sftp_cfg (dict): dictionary with user/host/pass where json file stay
        """

        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.connect(hostname=sftp_cfg['host'],
                         username=sftp_cfg['user'],
                         password=sftp_cfg['passwd'],
                         allow_agent=False)

        self.sftp = self.ssh.open_sftp()
        self.is_online = True
        self.path_remoto = ''

    def get_local(self) -> str:
        """Get local path

        Returns:
            str: path full
        """

        return self.path_remoto

    def get_path(self, path : str) -> str:
        """returns directory plus the parameter, and creates the same if there is no

        Args:
            path (str): directoru used to

        Returns:
            str: joined loca plus path, create directory if not exist
        """

        try:
            self.sftp.chdir(path)  # Test if remote_path exists
            self.path_remoto = path
        except IOError:
            self.sftp.mkdir(path)  # Create remote_path
            self.sftp.chdir(path)

        return path

    def __enter__(self):
        """Use as a context manager."""

        return self

    def __exit__(self, *err):
        """Leaving a context."""

        self.close()

    def close(self):
        """Close session"""

        if self.is_online:
            self.is_online = False
            try:
                self.sftp.close()
            except (Exception) as exp:
                pass

            try:
                self.ssh.close()
            except (Exception) as exp:
                pass

    def write_json(self, recordset : dict, file_name : str) -> bool:
        """Write a json file in sftp

        Args:
            recordset (dict): record
            file_name (str): file os json

        Returns:
            bool: _description_
        """

        try:
            with self.sftp.file(file_name,'w') as remote:
                remote.write(json.dumps(recordset, ensure_ascii=False))
                return True

        except Exception as exp:
            logger.error("transfer error: %s Erro: %s", file_name, str(exp.args))

        return False

    def list_files(self, pathfile : str) -> list[str]:
        """list of files in directory

        Args:
            pathfile (str): path

        Returns:
            list[str]: list of files
        """

        files :list[str] = []

        self.get_path(pathfile)

        for i in self.sftp.listdir():
            lstatout = str(self.sftp.lstat(i)).split()[0]
            if 'd' not in lstatout:
                files.append(i)

        return sorted(files)
