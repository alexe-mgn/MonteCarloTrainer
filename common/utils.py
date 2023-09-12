import logging
import sys
from os import getcwd
from os.path import normpath, abspath, join, dirname

__all__ = ['CONST', 'STATE', 'PATH']


class _Const:
    _LOGGER = 'meta'

    def __init__(self):
        logging.getLogger().warning(f"Instantiation of {self.__class__.__name__} detected.")
        raise NotImplementedError(f"{self.__class__.__name__} is not instantiable.")

    @classmethod
    def log_debug(cls):
        log = logging.getLogger(cls._LOGGER)
        log.debug(f'{cls.__module__}.{cls.__name__} MEMBERS:')
        for k in dir(cls):
            v = getattr(cls, k)
            if not k.startswith('__') and not hasattr(v, '__call__'):
                log.debug(f'\t{k}\t=\t{v}')


class CONST(_Const):
    BASE_NAME = "MonteCarloTrainer"


class STATE(_Const):
    FROZEN = getattr(sys, 'frozen', False)
    BUNDLED = FROZEN and getattr(sys, '_MEIPASS', None)
    HAS_CLIENT = False
    HAS_SERVER = False

    DEBUG = False


class PATH(_Const):
    EXECUTABLE = dirname(abspath(sys.argv[0]))
    CWD = getcwd()
    MEIPASS = getattr(sys, '_MEIPASS', EXECUTABLE)

    LOAD = MEIPASS
    WRITE = EXECUTABLE

    UTILS_FILE = __file__

    @classmethod
    def get(cls, *path, mode=None):
        if mode is None:
            return normpath(join(PATH.LOAD, *path))
        else:
            return normpath(join(getattr(cls, mode), *path))
