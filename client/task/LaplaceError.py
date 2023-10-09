import numpy as np
from scipy.stats import laplace


class LaplaceError:

    def __init__(self):
        ...

    def get_error(self, key: float):
        interval = laplace.interval(key)
        return interval[1] - interval[0]

    def get_table(self, center_key, dev: float = 0.1, n: int = 10):
        return [(k, self.get_error(k)) for k in np.linspace(
            max(0, center_key * (1 - dev)),
            min(1, center_key * (1 + dev)),
            n + (1 - n % 2)
        )[:-1 if not (n % 2) else None]]
