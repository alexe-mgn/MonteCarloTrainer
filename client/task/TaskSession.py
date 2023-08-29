import functools
import time
from typing import Self

from common.task.utils import STEP, ACTION, ERROR, ERRORS
from client.task.exceptions import TaskError
from client.task.Task import Task, Interval

Point = tuple[float, float]


class _ActionFunc:

    def __init__(self, func, action: ACTION):
        self.func = func
        self._action = action
        functools.update_wrapper(self, func)

    @property
    def action(self):
        return self._action

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)


class TaskSession:

    def __init__(self, task: Task):
        self._task = task

        self._step = STEP.START

        self._time = {}

        self._int_x: Interval | None = None
        self._int_y: Interval | None = None

        self._points = []
        self._points_hit = []
        self._point_counted = True

    @property
    def task(self):
        return self._task

    @property
    def step(self):
        return self._step

    def raise_for_step(self, step: STEP, code: ERROR):
        if self._step is not step:
            raise TaskError(code)

    @staticmethod
    def _action(action: ACTION):

        def decorator(func):
            return _ActionFunc(func, action)

        return decorator

    @staticmethod
    def _check_step(step: STEP, error: ERROR):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self: Self, *args, **kwargs):
                self.raise_for_step(step, error)
                return func(self, *args, **kwargs)

            return wrapper

        return decorator

    def start(self):
        if self._step is not STEP.START:
            raise UserWarning(f"{self} is already started at {self._time.get('start', None)}.")
        else:
            self._step = STEP.RECT
            self._time['start'] = time.time()

    def end(self):
        if self._step is STEP.END:
            raise UserWarning(f"{self} is already finished at {self._time.get('end', None)}")
        else:
            self._step = STEP.END
            self._time['end'] = time.time()

    def next_step(self):
        error = TaskError()
        nxt = None
        match self._step:
            case STEP.START:
                self.start()
            case STEP.RECT:  # TODO checks
                if self._int_x is None:
                    error |= ERRORS.RECT.X_0 | ERRORS.RECT.X_1
                if self._int_y is None:
                    error |= ERRORS.RECT.Y_0 | ERRORS.RECT.Y_1
                nxt = STEP.POINTS
            case STEP.POINTS:
                nxt = STEP.INTEGRAL
            case STEP.INTEGRAL:
                nxt = STEP.ERROR
            case STEP.ERROR:
                self.end()
            case _:
                raise RuntimeError(f"{self} can't switch from step {self._step}")
        if error:
            raise error
        elif nxt is not None:
            self._step = nxt

    def int_x(self) -> Interval | None:
        return self._int_x

    @_check_step(STEP.RECT, ERRORS.RECT.WRONG_STEP)
    @_action(ACTION.X_0 | ACTION.X_1)
    def set_int_x(self, interval: Interval):
        error = TaskError()
        if interval[0] != self._task.interval[0]:
            error |= ERRORS.RECT.X_0
        if interval[1] != self._task.interval[1]:
            error |= ERRORS.RECT.X_1
        if error:
            raise error
        else:
            self._int_x = tuple(interval)

    def int_y(self) -> Interval | None:
        return self._int_y

    @_check_step(STEP.RECT, ERRORS.RECT.WRONG_STEP)
    @_action(ACTION.Y_0 | ACTION.Y_1)
    def set_int_y(self, interval: Interval):
        error = TaskError()
        if interval[0] != self._task.interval[0]:  # TODO y checks
            error |= ERRORS.RECT.Y_0
        if interval[1] != self._task.interval[1]:
            error |= ERRORS.RECT.Y_1
        if error:
            raise error
        else:
            self._int_y = tuple(interval)

    def points(self) -> list[Point]:
        return list(self._points)

    def point_hits(self) -> list[bool]:
        return list(self._points_hit)

    @_check_step(STEP.POINTS, ERRORS.POINTS.WRONG_STEP)
    @_action(ACTION.GENERATE)
    def generate_point(self, p: Point):
        if not self._point_counted:
            raise TaskError(ERRORS.POINTS.GENERATE_BEFORE_COUNT)
        else:
            if not (self._int_x[0] <= p[0] <= self._int_x[1] and self._int_y[0] <= p[1] <= self._int_y[1]):
                raise TaskError(ERRORS.POINTS.POINT)
            else:
                self._points.append(tuple(p))
                self._point_counted = False

    @_check_step(STEP.POINTS, ERRORS.POINTS.WRONG_STEP)
    @_action(ACTION.COUNT)
    def count_point(self, hit: bool):
        if self._point_counted:
            raise TaskError(ERRORS.POINTS.COUNT_BEFORE_GENERATE)
        else:
            p = self._points[-1]
            y_f = self._task.f(p[0])
            hit_real = p[1] <= y_f
            if hit != hit_real:
                raise TaskError(ERRORS.POINTS.COUNT)
            else:
                self._points_hit.append(hit_real)
                self._point_counted = True

    def __repr__(self):
        return f"{self.__class__.__name__}({self._task}, step={self._step})"
