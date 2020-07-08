import base64
import tempfile
from datetime import datetime
import os
from contextlib import contextmanager
from pathlib import Path

from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient


@contextmanager
def scp(ssh_client: SSHClient):
    yield SCPClient(ssh_client.get_transport())


@contextmanager
def ssh(server):
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(
        server.host,
        username=server.user,
        key_filename=server.key_filename,
        look_for_keys=True,
        timeout=5000
    )
    try:
        yield client
    finally:
        client.close()


@contextmanager
def ssh_key(key, pub_key, key_fname):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_dir = Path(tmpdir)
        key_file = tmp_dir.joinpath(key_fname)
        with key_file.open('wb') as wh:
            wh.write(base64.b64decode(key.encode('utf8')))

        pubkey_file = tmp_dir.joinpath(key_fname + '.pub')
        with pubkey_file.open('wb') as wh:
            wh.write(base64.b64decode(pub_key.encode('utf8')))

        try:
            yield str(key_file)
        finally:
            pass


class RemoteServer:
    def __init__(self, host: str, user: str, key_filename: str):
        self.host = host
        self.user = user
        self.key_filename = key_filename

    def get(self, *args, **kwargs):
        with ssh(self) as client:
            with scp(client) as cp:
                cp.get(*args, **kwargs)

    def put(self, *args, **kwargs):
        with ssh(self) as client:
            with scp(client) as cp:
                cp.put(*args, **kwargs)

    @staticmethod
    def tstamp():
        return datetime.utcnow().strftime('%Y%m%d.%H%M%S')


@contextmanager
def ssh_cfg(**kwargs):
    """
    Generating temporary SSH config and dumps ssh keys in temp dir

    Parameters
    ----------
    host : str, 'localhost'
        SSH host, by default is None. If none trying to read env parameter `SSH_HOST`
    user : str, 'guest'
        SSH user, by default is None. If none trying to read env parameter `SSH_USER`
    pkey : str
        Private key, encoded by Base64, by default is None. If none trying to read env parameter `SSH_KEY`
    pub_key : str
        Public key, encoded by Base64, by default is None. If none trying to read env parameter `SSH_PUB_KEY`
    key_fname : str, 'id_rsa'
        Key filename, by default is `id_rsa`.

    Yields
    ------
    conf_path : str
        Temporary SSH Config file location
    """
    ssh_user = kwargs.get('user') or os.getenv('SSH_USER', 'guest')
    ssh_host = kwargs.get('host') or os.getenv('SSH_HOST', 'localhost')
    ssh_alias = kwargs.get('alias') or ssh_host
    ssh_pkey = base64.b64decode(kwargs.get('pkey') or os.getenv('SSH_KEY'))
    ssh_pub_key = base64.b64decode(kwargs.get('pub_key') or os.getenv('SSH_PUB_KEY'))
    ssh_key_fname = kwargs.get('key_fname') or os.getenv('SSH_KEY_FILE', 'id_rsa')

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_ = Path(tmpdir)

        pkey_path = tmpdir_.joinpath(ssh_key_fname)
        pubkey_path = tmpdir_.joinpath(ssh_key_fname + '.pub')
        conf_path = tmpdir_.joinpath('config')

        with pkey_path.open('wb') as wh:
            wh.write(ssh_pkey)

        with pubkey_path.open('wb') as wh:
            wh.write(ssh_pub_key)

        with conf_path.open('w') as wh:
            wh.write(f'''
Host {ssh_alias}
    IdentitiesOnly  yes
    AddKeysToAgent  yes
    HostName        {ssh_host}
    User            {ssh_user}
    IdentityFile    {pkey_path}
''')

        pkey_path.chmod(0o600)
        pubkey_path.chmod(0o600)
        conf_path.chmod(0o600)

        yield str(conf_path)
