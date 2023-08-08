from PySide6.QtWidgets import QWidget

from client.gui.UI.TaskWidget import Ui_TaskWidget
from client.gui.plot.PlotController import PlotController


class TaskWidget(QWidget, Ui_TaskWidget):

    def __init__(self):
        super().__init__()
        self.setupUi()

        self._plot_controller = PlotController(self.viewPlot)

    def setupUi(self, target=None):
        super().setupUi(self if target is None else target)
