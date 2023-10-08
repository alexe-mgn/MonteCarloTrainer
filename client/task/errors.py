import numpy as np
from scipy.stats import laplace


class LaplaceError:

    def __init__(self):
        ...

    def get_error(self, key: float):
        return laplace.interval(1 - key)[1]

    def get_table(self, center_key, dev: float = 0.1, n: int = 10):
        return [(k, self.get_error(k)) for k in np.linspace(
            max(0, center_key * (1 - dev)), min(1, center_key * (1 + dev)), n)]
