from subprocess import Popen, PIPE
import logging


def shexec(cmd, stdout=True) -> int or None:
    proc = Popen(
        cmd,
        stderr=PIPE,
        stdout=PIPE,
        shell=True,
        universal_newlines=True
    )

    logging.debug(cmd)

    if stdout:
        for line in proc.stdout:
            print(line.strip())

    for line in proc.stderr:
        logging.error(line)

    return proc.returncode
