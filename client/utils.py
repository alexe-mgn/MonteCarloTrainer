import sys
from os import getcwd
from os.path import normpath, abspath, join, dirname

__all__ = ['STATE', 'PATH']


class STATE:
    FROZEN = getattr(sys, 'frozen', False)
    BUNDLED = FROZEN and getattr(sys, '_MEIPASS', None)


class PATH:
    EXECUTABLE = dirname(abspath(sys.argv[0]))
    CWD = getcwd()
    MEIPASS = getattr(sys, '_MEIPASS', EXECUTABLE)
    CONFIG = dirname(abspath(__file__))

    LOAD = CONFIG
    WRITE = EXECUTABLE

    UI = join(LOAD, normpath('gui/UI'))

    def __init__(self):
        raise NotImplementedError('PATH is not instantiable')

    @classmethod
    def get(cls, *path, mode=None):
        if mode is None:
            return normpath(join(PATH.LOAD, *path))
        else:
            return normpath(join(getattr(cls, mode), *path))
