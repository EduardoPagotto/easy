# Easy

Facilitador de uso do TinyDB em SSHFS

Dependencias no Fedora 41
```bash
# instala CLI
sudo dnf install  sshfs

# set env
python3 -m venv .venv
source .venv/bin/activate

# install deps
pip3 install -r requirements.txt
```

Para teste
```bash
# Criar na maquina com usuario remote01 com password 'ZZZZZ'
sudo adduser remote01
sudo passwd remote01 'ZZZZZ'

# Entrar 1x para captura do ip
ssh remote01@127.0.0.1

# sai do usuario remoto
exit

# Configurar /etc/fuse.conf descomentado user_allow_other e salvar
sudo vim /etc/fuse.conf

# montagem na mao da unidade
sudo mkdir /mnt/shared

# Monta unidade
sshfs remote01@127.0.0.1:/home/remote01/ /mnt/shared -o password_stdin -o allow_other -o ro <<< 'ZZZZZ'

```
