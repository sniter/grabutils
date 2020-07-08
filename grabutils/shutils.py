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

    errors = False
    for line in proc.stderr:
        if not errors:
            logging.error(cmd)
            errors = True
        logging.error(line)

    return proc.returncode
