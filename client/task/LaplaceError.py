import numpy as np
from scipy.special import erf, erfinv


class LaplaceError:

    def __init__(self):
        ...

    @staticmethod
    def get_error(key: float):
        return erf(key / 2 ** .5) / 2

    @staticmethod
    def get_inverse(error: float):
        return 2 ** .5 * erfinv(2 * error)

    def get_table(self, rows=40, cols=10, step_y=0.1, step_x=0.01):
        x = np.arange(0, step_x * cols, step_x)
        y = np.arange(0, step_y * rows, step_y)
        x, y = np.meshgrid(x, y)
        return self.get_error(x + y)
