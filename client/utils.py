from os.path import normpath, abspath, join, dirname

from common.utils import CONST as COMMON_CONST, STATE as COMMON_STATE, PATH as COMMON_PATH

__all__ = ['CONST', 'STATE', 'PATH']

COMMON_STATE.HAS_CLIENT = True


class CONST(COMMON_CONST):
    CLIENT_NAME = COMMON_CONST.BASE_NAME + ' client'


class STATE(COMMON_STATE):
    DEBUG = COMMON_STATE.DEBUG


class PATH(COMMON_PATH):
    # CONFIG = MEIPASS

    LOAD = COMMON_PATH.LOAD
    # WRITE = EXECUTABLE

    UI = join(LOAD, normpath('gui/UI'))
    PLOT = join(LOAD, normpath('gui/plot'))
    PLOTLY_JS = join(PLOT, 'plotly.min.js')
    PLOT_HTML = join(PLOT, 'plot.html')

    UTILS_FILE = __file__
