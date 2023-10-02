from typing import Self
import functools

import time

from common.task.const import STEP, ACTION, ERROR, ERRORS, Interval, Point
from common.task.data import TaskState, TaskStats
from common.task.exceptions import TaskError
from client.task.Task import Task


class TaskSession:
    _RESOLUTION = 1000

    accuracy = 0.01
    y_accuracy = 0.1
    min_points = 10

    def __init__(self, task: Task):
        self._task = task

        self._f_min = None
        self._f_max = None
        start = self._task.interval[0]
        dist = self._task.interval[1] - self._task.interval[0]
        for i in range(self._RESOLUTION):
            x = start + dist * (i / self._RESOLUTION)
            y = self.task.f(x)
            if self._f_min is None or y < self._f_min:
                self._f_min = y
            if self._f_max is None or y > self._f_max:
                self._f_max = y

        self._state = self._create_state()
        self._stats = self._create_stats()

    def _create_state(self) -> TaskState:
        return TaskState()

    def _create_stats(self) -> TaskStats:
        return TaskStats(self._state)

    @property
    def task(self):
        return self._task

    @property
    def state(self):
        """
        IMMUTABLE
        :return:
        """
        return self._state

    @property
    def stats(self):
        """
        IMMUTABLE
        :return:
        """
        return self._stats

    def compare(self, trying: float, correct: float):
        return abs(correct - trying) / abs(correct) <= self.accuracy if correct != 0 else trying == correct

    @property
    def f_min(self):
        return self._f_min

    @property
    def f_max(self):
        return self._f_max

    @property
    def step(self):
        return self._state.step

    def raise_for_step(self, step: STEP, code: ERROR):
        if self._state.step is not step:
            raise TaskError(code)

    @staticmethod
    def _action(action: ACTION):

        def decorator(func):
            @functools.wraps(func)
            def wrapper(self: Self, *args, **kwargs):
                res = func(self, *args, **kwargs)
                self._record_action(action, args, kwargs)
                self._notify_action(action, args, kwargs)
                return res

            return wrapper

        return decorator

    def _record_action(self, action: ACTION, args: tuple, kwargs: dict):
        self._stats.append_action(action, args, kwargs)

    def _notify_action(self, action: ACTION, args: tuple, kwargs: dict):
        pass

    @staticmethod
    def _check_error(step: STEP | None = None, code: ERROR = ERROR(0)):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self: Self, *args, **kwargs):
                try:
                    if step is not None:
                        self.raise_for_step(step, code)
                    return func(self, *args, **kwargs)
                except TaskError as error:
                    self._record_error(error.code, args, kwargs)
                    self._notify_error(error.code, args, kwargs)

            return wrapper

        return decorator

    def _record_error(self, error: ERROR, args: tuple, kwargs: dict):
        self._stats.append_error(error, args, kwargs)  # TODO Resolve zero error.

    def _notify_error(self, error: ERROR, args: tuple, kwargs: dict):
        if error:
            raise TaskError(error)

    def start(self):
        if self._state.step is not STEP.START:
            raise UserWarning(f"{self} is already started at {self._stats.step_time.get(STEP.START, None)}.")
        else:
            self.next_step()

    def end(self):
        if self._state.step is STEP.END:
            raise UserWarning(f"{self} is already finished at {self._stats.step_time.get(STEP.END, None)}")
        else:
            self._stats.step_time[STEP.END] = time.time()
            self._state.step = STEP.END
            self._record_action(ACTION.END, (), {})
            self._notify_action(ACTION.END, (), {})

    @_check_error()
    def next_step(self):
        state = self._state

        error = TaskError()
        # nxt = None
        match state.step:
            case STEP.START:
                nxt = STEP.RECT
                action = ACTION.START
            case STEP.RECT:
                if state.int_x is None:
                    error |= ERRORS.RECT.X_0 | ERRORS.RECT.X_1
                if state.int_y is None:
                    error |= ERRORS.RECT.Y_0 | ERRORS.RECT.Y_1
                nxt = STEP.POINTS
                action = ACTION.RECT_COMPLETE
            case STEP.POINTS:
                if not state.point_counted:
                    error |= ERRORS.POINTS.COMPLETE_BEFORE_COUNT
                elif len(state.points) < self.min_points:
                    error |= ERRORS.POINTS.NOT_ENOUGH_POINTS
                nxt = STEP.INTEGRAL
                action = ACTION.POINTS_COMPLETE
            case STEP.INTEGRAL:
                if state.result is None:
                    error |= ERRORS.INTEGRAL.RESULT
                nxt = STEP.END
                action = ACTION.INTEGRAL_COMPLETE | ACTION.END
            case STEP.ERROR:
                raise NotImplementedError(f"{self} doesn't implement step {STEP.ERROR}")
            case _:
                raise RuntimeError(f"{self} can't switch from step {state.step}")
        if error:
            raise error
        elif nxt is not None:
            if nxt != state.step:
                self._stats.step_time[nxt] = time.time()
            state.step = nxt
            self._record_action(action, (), {})
            self._notify_action(action, (), {})

    @_check_error(STEP.RECT, ERRORS.RECT.WRONG_STEP)
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
            self._state.int_x = tuple(interval)

    @_check_error(STEP.RECT, ERRORS.RECT.WRONG_STEP)
    @_action(ACTION.Y_0 | ACTION.Y_1)
    def set_int_y(self, interval: Interval):
        error = TaskError()
        y_allowed_error = (self._f_max - self._f_min) * self.y_accuracy
        y_min = self._f_min
        if not y_min - y_allowed_error <= interval[0] <= y_min:
            error |= ERRORS.RECT.Y_0
        y_max = self._f_max
        if not y_max <= interval[1] <= y_max + y_allowed_error:
            error |= ERRORS.RECT.Y_1
        if error:
            raise error
        else:
            self._state.int_y = tuple(interval)

    @_check_error(STEP.POINTS, ERRORS.POINTS.WRONG_STEP)
    @_action(ACTION.GENERATE)
    def generate_point(self, p: Point):
        if not self._state.point_counted:
            raise TaskError(ERRORS.POINTS.GENERATE_BEFORE_COUNT)
        else:
            if not (self._state.int_x[0] <= p[0] <= self._state.int_x[1] and self._state.int_y[0] <= p[1] <=
                    self._state.int_y[1]):
                raise TaskError(ERRORS.POINTS.POINT)
            else:
                self._state.points.append(tuple(p))
                self._state.point_counted = False

    def discard_point(self):
        if self._state.point_counted:
            raise RuntimeError(f"{self}: No uncounted points to discard.")
        else:
            self._state.points.pop()
            self._state.point_counted = True

    @_check_error(STEP.POINTS, ERRORS.POINTS.WRONG_STEP)
    @_action(ACTION.COUNT)
    def count_point(self, hit: bool):
        if self._state.point_counted:
            raise TaskError(ERRORS.POINTS.COUNT_BEFORE_GENERATE)
        else:
            p = self._state.points[-1]
            y_f = self._task.f(p[0])
            hit_real = p[1] <= y_f
            if hit != hit_real:
                raise TaskError(ERRORS.POINTS.COUNT |
                                (ERRORS.POINTS.COUNT_HIT if
                                 hit else
                                 ERRORS.POINTS.COUNT_MISS))
            else:
                self._state.point_hits.append(hit_real)
                self._state.point_counted = True

    @_check_error(STEP.INTEGRAL, ERRORS.INTEGRAL.WRONG_STEP)
    @_action(ACTION.RESULT)
    def set_result(self, res: float):
        state = self._state
        area = (state.int_x[1] - state.int_x[0]) * (state.int_y[1] - state.int_y[0])
        area_neg = (state.int_x[1] - state.int_x[0]) * max(0.0, -state.int_y[0])
        res_true = area * (sum(state.point_hits) / len(state.points)) - area_neg
        if not self.compare(res, res_true):
            raise TaskError(ERRORS.INTEGRAL.RESULT)
        else:
            state.result = res

    def __repr__(self):
        return f"{self.__class__.__name__}({self._task}, step={self._state.step})"
