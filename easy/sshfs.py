'''
Created on 20241209
Update on 20250210
@author: Eduardo Pagotto
'''

import logging
import os
from pathlib import Path
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)

__all__ = ('SSHFS', 'desmontar')

def desmontar(mount_point :str, log_data : bool = True) -> bool:
    """Desmonta unidade SSHDFS

    Args:
        mount_map (str): ponde de desmontagem

    Returns:
        bool: True se sucesso
    """
    try:
        if log_data:
            logger.info('umount %s', mount_point)

        result = subprocess.run(f"umount {mount_point}",
                            text=True,
                            shell=True,
                            capture_output=True,
                            executable='/bin/sh')

        if result.returncode != 0:
            if log_data:
                logger.warning('stderr: %s', result.stderr.replace('\n',''))
        else:
            return True

    except Exception as exp:
        logger.error("umount %s falhou", str(exp.args))

    return False

class SSHFS(object):
    def __init__(self, conn : dict, ro: bool, local : Optional[str] = None):
        """Monta unidade remota localmente com SSHFS

        Args:
            conn (dict): Configuracoes de conexao e locais de acesso e montagem local
            ro (bool): True monta remoto como Read Only
            local (Optional[str], optional): Se dado sobrescreve montagem local FULL. Defaults to None.
        """

        self.conn = conn
        self.ro = ro
        #self.log = logging.getLogger('OCP2.SSHFS')
        self.local = self.conn['local'] if not local else local

        # Forca a desmontagem e criacao do diretorio
        try:
            # Cria Diretorio se não existe e desmonta share se app em reset
            if Path(self.local).is_dir():
                desmontar(self.local, False)
            else:
                logger.info('criar diretorio de montagem: %s', self.local)
                Path(self.local).mkdir(parents=True, exist_ok=True)
        except:
            desmontar(self.local)

    def get_local(self) -> str:
        """Retona o path montado

        Returns:
            str: path full
        """
        return self.local

    def get_path(self, path : str) -> str:
        """retorna o diretorio montado mais o parametro, e cria o mesmo se nao exitir

        Args:
            path (str): diretorio a ser usado

        Returns:
            str: combinação do local mais o path passado
        """

        new_path = os.path.join(self.get_local(), path)
        if os.path.isdir(new_path):
            logger.info('path remoto adquirido: %s', new_path)
            return new_path

        Path(new_path).mkdir(parents=True, exist_ok=True)
        logger.warning('path remoto criado: %s', new_path)
        return new_path


    def __enter__(self):
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
                #logger.error('stderr: %s', result.stderr)
                #logger.error('stdout: %s', result.stdout)
                raise Exception(f"Falha na montagem: {result.stderr}")

        except Exception as exp:
            raise Exception(str(exp.args))

        return self

    def __exit__(self, *err):
        desmontar(self.local)
