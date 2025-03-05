# Easy

TinyDB in SSHFS

Dependencies of Fedora 41
```bash
# instala CLI
sudo dnf install sshfs

# set env
python3 -m venv .venv
source .venv/bin/activate

# install deps
pip3 install -r requirements.txt
```

To test
```bash
# Create user in host remote01 and password 'ZZZZZ'
sudo adduser remote01
sudo passwd remote01 'ZZZZZ'

exit

# Config /etc/fuse.conf uncoment user_allow_other
sudo vim /etc/fuse.conf

# create a mount point
sudo mkdir /mnt/shared

# Manualy mount
sshfs remote01@127.0.0.1:/home/remote01/ /mnt/shared -o password_stdin -o allow_other -o ro <<< 'ZZZZZ'

```
