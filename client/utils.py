import sys
from os import getcwd
from os.path import normpath, abspath, join, dirname

__all__ = ['STATE', 'PATH']


class STATE:
    FROZEN = getattr(sys, 'frozen', False)
    BUNDLED = FROZEN and getattr(sys, '_MEIPASS', None)
    DEBUG = True


class PATH:
    EXECUTABLE = dirname(abspath(sys.argv[0]))
    CWD = getcwd()
    MEIPASS = getattr(sys, '_MEIPASS', EXECUTABLE)
    # CONFIG = dirname(abspath(__file__))
    CONFIG = MEIPASS

    LOAD = CONFIG
    WRITE = EXECUTABLE

    UI = join(LOAD, normpath('gui/UI'))
    PLOT = join(LOAD, normpath('gui/plot'))
    PLOTLY_JS = join(PLOT, 'plotly.min.js')
    PLOT_HTML = join(PLOT, 'plot.html')

    FILE = __file__

    def __init__(self):
        raise NotImplementedError('PATH is not instantiable')

    @classmethod
    def get(cls, *path, mode=None):
        if mode is None:
            return normpath(join(PATH.LOAD, *path))
        else:
            return normpath(join(getattr(cls, mode), *path))
