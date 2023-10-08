from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

from common.task.data import TaskState
from client.task.errors import LaplaceError


class ErrorTableWidget(QTableWidget):

    def __init__(self, center_key: float, rows=10, cols=2, dev: float = 0.1):
        super().__init__()
        self.setRowCount(rows)
        self.setColumnCount(2 * cols)
        self.setHorizontalHeaderLabels(['Доверительный\nинтервал', 'Обратное\nраспределение\nЛапласа'] * cols)
        for n, (key, value) in enumerate(LaplaceError().get_table(center_key, dev=dev, n=rows*cols)):
            row = n % rows
            col = n // rows
            key_item = QTableWidgetItem(f'{key:.3g}')
            key_item.setFlags(key_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, col * 2, key_item)
            value_item = QTableWidgetItem(f'{value:.3g}')
            value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, col * 2 + 1, value_item)
