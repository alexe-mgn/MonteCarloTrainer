import numpy as np

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout

from common.user_math import LaplaceError


class ErrorTableWidget(QWidget):

    def __init__(self, laplace: LaplaceError):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.header_widget = QLabel(
            "Таблица значений функции Лапласа L(x)\n"
            "строка - десятые x\n"
            "столбец - сотые x\n"
            "значение - доверительная вероятность")
        self.header_widget.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.layout().addWidget(self.header_widget)
        self.table_widget = QTableWidget()
        self.layout().addWidget(self.table_widget)

        self.table_widget.setSizeAdjustPolicy(self.table_widget.SizeAdjustPolicy.AdjustToContents)
        rows, cols = laplace.rows, laplace.cols
        step_y, step_x = laplace.step_y, laplace.step_x
        self.table_widget.setRowCount(rows)
        self.table_widget.setColumnCount(cols)
        self.table_widget.setHorizontalHeaderLabels(['{:.3g}'.format(e) for e in np.arange(0, cols * step_x, step_x)])
        self.table_widget.setVerticalHeaderLabels(['{:.3g}'.format(e) for e in np.arange(0, rows * step_y, step_y)])
        for rows, cols, values in zip(
                *np.mgrid[:rows, :cols],
                laplace.get_table()):
            for row, col, value in zip(rows, cols, values):
                value_item = QTableWidgetItem(f'{value:.4g}')
                value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table_widget.setItem(row, col, value_item)
