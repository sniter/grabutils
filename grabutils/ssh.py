import base64
import tempfile
from datetime import datetime

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
