from typing import Callable

import sympy
from sympy.parsing.sympy_parser import *

from client.exceptions import AppError

Interval = tuple[float, float]
Function = Callable[[float], float]


class Task:
    _parser_transformations = standard_transformations + (split_symbols, implicit_multiplication, convert_xor)

    def __init__(self, f: str | sympy.Expr, interval: Interval):
        try:
            if not isinstance(f, sympy.Expr):
                f = sympy.parse_expr(f, evaluate=False, transformations=self._parser_transformations)
            else:
                ...
        except ValueError or SyntaxError as e:
            raise AppError(f"Невозможно обработать выражение \"{f}\".") from e
        f: sympy.Expr
        if len(f.free_symbols) > 1:
            raise AppError(f"Слишком много переменных (\"{f.free_symbols}\") в выражении \"{f}\".")
        self._f_expr = f
        self._f_sym = f.free_symbols.pop() if f.free_symbols else sympy.Symbol('x')
        self._f_eval = sympy.lambdify(self._f_sym, f)
        self._interval = tuple(interval)  # TODO Comparison

    @property
    def f_expr(self) -> sympy.Expr:
        return self._f_expr

    def f_call(self, x: float) -> float:
        return float(self._f_eval(x))

    @property
    def f(self) -> Function:
        return self.f_call

    @property
    def interval(self) -> Interval:
        return self._interval

    def f_unicode_str(self):
        return sympy.pretty(self._f_expr, use_unicode=True)

    def unicode_str(self):
        return sympy.pretty(
            sympy.Integral(self._f_expr,
                           (self._f_sym, *self._interval)),
            use_unicode=True)
