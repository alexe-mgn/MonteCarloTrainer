from typing import Callable

import sympy

from client.exceptions import AppError

Interval = tuple[float, float]


class Task:

    def __init__(self, f: str | sympy.Expr, interval: Interval):
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
    def f_expr(self) -> sympy.Expr:
        return self._f_expr

    @property
    def f(self) -> Callable[[float], float]:  # TODO Vectorized
        return self._f_eval

    @property
    def interval(self) -> Interval:
        return self._interval
