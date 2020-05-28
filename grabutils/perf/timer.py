import os
import time
import sys
import math
import logging


# Taken from here: https://github.com/ipython/ipython/blob/master/IPython/core/magics/execution.py

def _format_time(timespan, precision=3):
    """Formats the timespan in a human readable form"""

    if timespan >= 60.0:
        # we have more than a minute, format that in a human readable form
        # Idea from http://snipplr.com/view/5713/
        parts = [("d", 60 * 60 * 24), ("h", 60 * 60), ("min", 60), ("s", 1)]
        times = []
        leftover = timespan
        for suffix, length in parts:
            value = int(leftover / length)
            if value > 0:
                leftover = leftover % length
                times.append(u'%s%s' % (str(value), suffix))
            if leftover < 1:
                break
        return " ".join(times)

    # Unfortunately the unicode 'micro' symbol can cause problems in
    # certain terminals.
    # See bug: https://bugs.launchpad.net/ipython/+bug/348466
    # Try to prevent crashes by being more secure than it needs to
    # E.g. eclipse is able to print a µ, but has no sys.stdout.encoding set.
    units = [u"s", u"ms", u'us', "ns"]  # the save value
    if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
        try:
            u'\xb5'.encode(sys.stdout.encoding)
            units = [u"s", u"ms", u'\xb5s', "ns"]
        except:
            pass
    scaling = [1, 1e3, 1e6, 1e9]

    if timespan > 0.0:
        order = min(-int(math.floor(math.log10(timespan)) // 3), 3)
    else:
        order = 3
    return u"%.*g %s" % (precision, timespan * scaling[order], units[order])


try:
    import resource


    def clock():
        """clock() -> floating point number
        Return the *TOTAL USER+SYSTEM* CPU time in seconds since the start of
        the process.  This is done via a call to resource.getrusage, so it
        avoids the wraparound problems in time.clock()."""

        u, s = resource.getrusage(resource.RUSAGE_SELF)[:2]
        return u + s


    def clock2():
        """clock2() -> (t_user,t_system)
        Similar to clock(), but return a tuple of user/system times."""
        return resource.getrusage(resource.RUSAGE_SELF)[:2]
except ImportError:
    # There is no distinction of user/system time under windows, so we just use
    # time.perff_counter() for everything...
    clock = time.perf_counter


    def clock2():
        """Under windows, system CPU time can't be measured.
        This just returns perf_counter() and zero."""
        return time.perf_counter(), 0.0


def timer(fn):
    def __wrap(*args, **kwargs):
        wtime = time.time
        wall_st = wtime()
        st = clock2()
        res = fn(*args, **kwargs)
        end = clock2()
        wall_end = wtime()
        wall_time = wall_end - wall_st
        cpu_user = end[0] - st[0]
        cpu_sys = end[1] - st[1]
        cpu_tot = cpu_user + cpu_sys
        if sys.platform != 'win32':
            print("CPU times: user %s, sys: %s, total: %s" % \
                  (_format_time(cpu_user), _format_time(cpu_sys), _format_time(cpu_tot)))
        print("Wall time: %s" % _format_time(wall_time))
        return res

    return __wrap


class Timer:
    wtime = time.time
    logger = logging.getLogger(__name__)

    @classmethod
    def wrap(cls, fn):
        def wrapper(*args, **kwargs):
            with Timer():
                res = fn(*args, **kwargs)
            return res

        return wrapper

    def __repr__(self):
        ret = ""
        if sys.platform != 'win32':
            ret += f"CPU times: user {_format_time(self.cpu_user)}, sys: {_format_time(self.cpu_sys)}, total: {_format_time(self.cpu_tot)}\n"
        ret += f"Wall time: {_format_time(self.wall_time)}\n"
        return ret

    def __init__(self):
        self.wall_start = None
        self.wall_end = None
        self.start = None
        self.end = None

        self.wall_time = None
        self.cpu_user = None
        self.cpu_sys = None
        self.cpu_tot = None

    def __enter__(self):
        self.wall_start = self.wtime()
        self.start = clock2()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wall_end = self.wtime()
        self.end = clock2()

        self.wall_time = self.wall_end - self.wall_start
        self.cpu_user = self.end[0] - self.start[0]
        self.cpu_sys = self.end[1] - self.start[1]
        self.cpu_tot = self.cpu_user + self.cpu_sys

        logging.debug(repr(self))
