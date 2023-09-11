from PySide6.QtWidgets import QWidget, QLCDNumber, QGridLayout

from client.exceptions import AppError
from common.task.const import STEP
from common.task.data import TaskStats


class StatsController:
    _view_map = {
        STEP.RECT: (
            'viewStats_1',
            'viewStats_6',
            'viewStats_11'
        ),
        STEP.POINTS: (
            'viewStats_2',
            'viewStats_7',
            'viewStats_12'
        ),
        STEP.INTEGRAL: (
            'viewStats_3',
            'viewStats_8',
            'viewStats_13'
        ),
        STEP.ERROR: (
            'viewStats_4',
            'viewStats_9',
            'viewStats_14'
        ),
        None: (
            'viewStats_5',
            'viewStats_10',
            'viewStats_15'
        ),
    }

    def __init__(self, w: QWidget):
        self._stats_widget = w
        self._stats_widget.label_4.hide()
        for i in range(len(self._view_map.get(STEP.ERROR, ()))):
            self._get_view(STEP.ERROR, i).hide()
        l: QGridLayout = self._stats_widget.layoutStats
        l.setColumnStretch(4, 0)

    def _get_view(self, step: STEP | None, t: int) -> QLCDNumber:
        if step not in self._view_map:
            raise AppError(f"Не заданы виджеты для отображения статистики по этапу {step}.")
        elif not 0 <= t < len(sw := self._view_map[step]):
            raise AppError(f"Не задано название виджета для отображения статистики по этапу {step}, индекс {t}.")
        elif not hasattr(self._stats_widget, vn := sw[t]):
            raise AppError(f"Не найден виджет \"{vn}\" для отображения статистики по этапу {step}, индекс {t}.")
        else:
            return getattr(self._stats_widget, vn)

    def set_stats(self, stats: TaskStats):
        gv = self._get_view
        for step in self._view_map.keys():
            if step is not None:
                gv(step, 0).display(int(step == stats.state.step))
                gv(step, 1).display(int(step < stats.state.step))
                gv(step, 2).display(len(stats.errors.get(step, ())))
        gv(None, 0).display(int(stats.state.step != STEP.END))
        gv(None, 1).display(int(stats.state.step == STEP.END))
        gv(None, 2).display(sum(map(len, stats.errors.values())))
