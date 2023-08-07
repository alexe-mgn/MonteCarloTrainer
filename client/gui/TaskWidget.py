from PySide6.QtWidgets import QWidget

from client.gui.UI.TaskWidget import Ui_TaskWidget


class TaskWidget(QWidget, Ui_TaskWidget):

    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self, target=None):
        super().setupUi(self if target is None else target)
