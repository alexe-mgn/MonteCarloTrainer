from typing import Self

from common.task.utils import STEP, ERROR


class TaskError(Exception):

    def __init__(self, step: STEP = None, error: ERROR = 0):
        super().__init__()
        self._step = step
        self._error = error

    def __bool__(self):
        return bool(self._error)

    def __ior__(self, other: ERROR | Self):
        other_error = other._error if isinstance(other, self.__class__) else other
        self._error |= other_error
