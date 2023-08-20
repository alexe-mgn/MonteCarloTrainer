import functools

import time

import sympy

from client.exceptions import AppError
from client.task.exceptions import TaskError
from common.task.utils import STEP, ERROR, ERRORS


class Task:

    def __init__(self, f: str | sympy.Expr, interval: tuple[float, float]):
        try:
            if not isinstance(f, sympy.Expr):
                f = sympy.parse_expr(f)
            else:
                ...
        except ValueError or SyntaxError as e:
            raise AppError(f"Невозможно обработать выражение \"{f}\".") from e
        f: sympy.Expr
        if len(f.free_symbols) > 1:
            raise AppError(f"Слишком много переменных (\"{f.free_symbols}\") в выражении \"{f}\".")
        self._f_expr = f
        self._f_eval = sympy.lambdify(f.free_symbols if f.free_symbols else sympy.Symbol('x'), f)
        self._interval = tuple(interval)

    @property
    def f_expr(self):
        return self._f_expr

    @property
    def f(self):
        return self._f_eval

    @property
    def interval(self):
        return self._interval


class TaskSession:

    def __init__(self, task: Task):
        self._task = task

        self._step = STEP.START

        self._time = {}

        self._int_x = None
        self._int_y = None

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
        if self._step != step:
            raise TaskError(self._step, code)

    @staticmethod
    def check_step(step: STEP, error: ERROR):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                self.raise_for_step(step, error)
                return func(self, *args, **kwargs)

            return wrapper

        return decorator

    def start(self):
        if self._step != STEP.START:
            raise UserWarning(f"{self} is already started at {self._time.get('start', None)}.")
        else:
            self._step = STEP.RECT
            self._time['start'] = time.time()

    def end(self):
        if self._step == STEP.END:
            raise UserWarning(f"{self} is already finished at {self._time.get('end', None)}")
        else:
            self._step = STEP.END
            self._time['end'] = time.time()

    def next_step(self):
        error = TaskError(self._step)
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

    @check_step(STEP.RECT, ERRORS.RECT.WRONG_STEP)
    def set_int_x(self, interval: tuple[float, float]):
        error = TaskError(self._step)
        if interval[0] != self._task.interval[0]:
            error |= ERRORS.RECT.X_0
        if interval[1] != self._task.interval[1]:
            error |= ERRORS.RECT.X_1
        if error:
            raise error
        else:
            self._int_x = tuple(interval)

    @check_step(STEP.RECT, ERRORS.RECT.WRONG_STEP)
    def set_int_y(self, interval: tuple[float, float]):
        error = TaskError(self._step)
        if interval[0] != self._task.interval[0]:  # TODO y checks
            error |= ERRORS.RECT.Y_0
        if interval[1] != self._task.interval[1]:
            error |= ERRORS.RECT.Y_1
        if error:
            raise error
        else:
            self._int_y = tuple(interval)

    @check_step(STEP.POINTS, ERRORS.POINTS.WRONG_STEP)
    def generate_point(self, p: tuple[float, float]):
        if not self._point_counted:
            raise TaskError(self._step, ERRORS.POINTS.GENERATE_BEFORE_COUNT)
        else:
            if not (self._int_x[0] <= p[0] <= self._int_x[1] and self._int_y[0] <= p[1] <= self._int_y[1]):
                raise TaskError(self._step, ERRORS.POINTS.POINT)
            else:
                self._points.append(tuple(p))
                self._point_counted = False

    @check_step(STEP.POINTS, ERRORS.POINTS.WRONG_STEP)
    def count_point(self, hit: bool):
        if self._point_counted:
            raise TaskError(self._step, ERRORS.POINTS.COUNT_BEFORE_GENERATE)
        else:
            p = self._points[-1]
            y_f = self._task.f(p[0])
            hit_real = p[1] <= y_f
            if hit != hit_real:
                raise TaskError(self._step, ERRORS.POINTS.COUNT)
            else:
                self._points_hit.append(hit_real)
                self._point_counted = True

    def __repr__(self):
        return f"{self.__class__.__name__}({self._task}, step={self._step})"
