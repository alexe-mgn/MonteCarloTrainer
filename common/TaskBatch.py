import csv
from typing import TextIO

from common.exceptions import AppError

BatchTaskTupleL = 7
BatchTaskTuple = tuple[str, str, float, float, int, float, float]
TaskBatch = list[BatchTaskTuple]


ERROR_STR = "Строки файла с заданием должны иметь следующий вид:" \
            " \"ФИО,Функция,Начало,Конец,Количество точек,Погрешность,Доверительный интервал\"." \
            " Синтаксис функций определяется библиотекой sympy (https://www.sympy.org/)." \
            " Ошибка в строке {n}: \"{row}\"."


def read_task_batch(io: TextIO, **kwargs) -> TaskBatch:
    batch = []
    reader = csv.reader(io, **kwargs)
    n = 0
    row = ''
    try:
        for n, row in enumerate(reader):
            assert len(row) == BatchTaskTupleL
            name = row[0]
            f = row[1]
            start, end = float(row[2]), float(row[3])
            min_points = int(row[4])
            error, confidence = float(row[5]), float(row[6])
            batch.append((name, f, start, end, min_points, error, confidence))
    except Exception as error:
        raise AppError(ERROR_STR.format(n=n, row=row)) from error
    return batch
