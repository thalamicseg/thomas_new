import subprocess
import signal
import multiprocessing.pool


class PoolWrapper(object):
    """
    Wraps a function to permit KeyboardInterrupt with a multiprocessing.Pool without traceback.
    Graceful exit will finish the job first before quitting, may only work in Unix-like system.
    Supports unpacking of arguments from tuples or keywords from dictionaries.
    """
    def __init__(self, func, graceful=False, unpack=True):
        self.func = func
        self.graceful = graceful
        self.unpack = unpack

    def __call__(self, args):
        if self.graceful:
            s = signal.signal(signal.SIGINT, signal.SIG_IGN)
            result = self._execute(args)
            signal.signal(signal.SIGINT, s)
            return result
        else:
            try:
                return self._execute(args)
            except KeyboardInterrupt:
                # Don't print out traceback.
                pass

    def _execute(self, args):
        if self.unpack:
            if isinstance(args, dict):
                return self.func(**args)
            return self.func(*args)
        else:
            return self.func(args)


class BetterPool(multiprocessing.pool.Pool):
    """
    A modification of multiprocessing.pool.Pool with map methods that properly receive keyboard
    interrupts.  By default, it will unpack tuple or dictionary arguments for the function call.
    """
    def _wrap(self, func, iterable):
        if iterable:
            if not isinstance(func, PoolWrapper):
                if isinstance(iterable[0], tuple) or isinstance(iterable[0], dict):
                    func = PoolWrapper(func, unpack=True)
                else:
                    func = PoolWrapper(func, unpack=False)
        return func

    def map_async(self, func, iterable, *args, **kwargs):
        func = self._wrap(func, iterable)
        return super(BetterPool, self).map_async(func, iterable, *args, **kwargs)

    def map(self, func, iterable, *args, **kwargs):
        p = self.map_async(func, iterable, *args, **kwargs)
        try:
            return p.get(0xFFFFFF)
        except KeyboardInterrupt:
            self.terminate()
            raise


def command(cmd, echo=False, verbose=False, debug=False, suppress=False, env=None):
    # sp_cmd = cmd.split(' ')
    if echo:
        print cmd
        return
    if verbose:
        print 'Executing: %s' % cmd
    if debug:
        # Workaround for Python 2/3
        try:
            input = raw_input
        except NameError:
            pass
        print 'About to run: %s' % cmd
        if input('  Type n to skip') == 'n':
            return
    if suppress:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, env=env)
        stdout, stderr = p.communicate()
        if stderr:
            print stderr
        return p.returncode
    # return subprocess.call(sp_cmd)
    return subprocess.call(cmd, shell=True, env=env)


if __name__ == "__main__":
    def sleep(time, num):
        command('sleep %s' % time)
        #time.sleep(seconds)
        print 'sleep %s' % num
        return 'Finished %s' % num

    pool = BetterPool(3)
    p = pool.map(sleep, [(10+i, i) for i in range(3)])
    # print p.get(0xFFFF)
