from typing import Self

from common.task.const import ACTION, ERROR


class TaskError(Exception):

    def __init__(self, code: ERROR = ERROR(0)):
        super().__init__()
        self.code = code

    def __bool__(self):
        return bool(self.code)

    def __ior__(self, other: ERROR | Self):
        if isinstance(other, self.__class__):
            self.code |= other.code
        else:
            self.code |= other
        return self

    def __contains__(self, item: ERROR):
        return item in self.code

    def __repr__(self):
        return f"{self.__class__.__name__}({self.code})"

    def __str__(self):
        return repr(self)
