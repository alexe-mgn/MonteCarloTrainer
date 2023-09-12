import csv

from common.exceptions import AppError

BatchTaskTuple = tuple[str, str, float, float]
TaskBatch = list[BatchTaskTuple]


ERROR_STR = "Строки файла с заданием должны иметь следующий вид: \"ФИО;Функция;Начало;Конец\"." \
            " Синтаксис функций определяется библиотекой sympy (https://www.sympy.org/)." \
            " Ошибка в строке {n}: \"{row}\"."


def read_task_batch(filepath: str, delimiter: str | None = None) -> TaskBatch:
    batch = []
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, **(dict(delimiter=delimiter) if delimiter is not None else dict()))
        try:
            for n, row in enumerate(reader):
                assert len(row) == 4
                name = row[0]
                f = row[1]
                start, end = float(row[2]), float(row[3])
                batch.append((name, f, start, end))
        except Exception as error:
            raise AppError(ERROR_STR.format(n=n, row=row)) from error
    return batch
