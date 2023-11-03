import math

import numpy as np
from scipy.special import erf, erfinv


def meaning_power(x: float):
    return math.floor(math.log10(math.fabs(x))) if x != 0 else 0


def meaning_decimals(x: float, dec: int = 1, frac_only: bool = True):
    mp = -meaning_power(x) + (dec - 1)
    return max(0, mp) if frac_only else mp


def round_meaning(x: float, dec: int, frac_only: bool = True):
    return round(x, meaning_decimals(x, dec=dec, frac_only=frac_only))


# def compare_decimals(x: float, y: float, dec: int):
#     return round(x, dec) == round(y, dec)


def compare_meaning(x: float, y: float, dec: int, frac_only: bool = True):
    md = max(meaning_decimals(e, dec=dec, frac_only=frac_only) for e in (x, y))
    return round(x, md) == round(y, md)


class LaplaceError:

    def __init__(self, rows=40, cols=10, step_y=0.1, step_x=0.01):
        self.rows = rows
        self.cols = cols
        self.step_y = step_y
        self.step_x = step_x

    @staticmethod
    def get_error(key: float):
        return erf(key / 2 ** .5) / 2

    @staticmethod
    def get_inverse(error: float):
        return 2 ** .5 * erfinv(2 * error)

    def get_args_y(self):
        return np.arange(0, self.step_y * self.rows, self.step_y)

    def get_args_x(self):
        return np.arange(0, self.step_x * self.cols, self.step_x)

    def get_table(self):
        x, y = np.meshgrid(self.get_args_x(), self.get_args_y())
        return self.get_error(x + y)

    def get_table_error(self, key: float):
        raise NotImplementedError()

    def get_table_inverse(self, error: float, n: int = 2):
        t = self.get_table()
        vs = np.argpartition(np.abs(t - error), n, axis=None)
        ys, xs = np.unravel_index(vs[:n], t.shape)
        y_args, x_args = self.get_args_y(), self.get_args_x()
        return y_args[ys] + x_args[xs]
