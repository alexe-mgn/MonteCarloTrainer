import json
import logging

from PySide6.QtCore import QUrl, QEvent, QObject, Qt, Signal
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QMainWindow

from client.task.Task import Function, Task
from client.task.TaskSession import Point
from client.utils import STATE, PATH


class PlotController(QObject):
    F_PLOT_POINTS = 1000
    F_PLOT_MARGIN = 0.2

    loaded = Signal()

    def __init__(self, view: QWebEngineView):
        super().__init__()
        self._view = view
        self._plot_page = PlotPage(self)
        self._plot_page.loadFinished.connect(self._load_finished)

        if STATE.DEBUG:
            self._dev_window = DevToolsWindow(self._plot_page.devToolsPage())
            self._dev_window.show()
        self.load_page()

    def _load_finished(self):
        self.loaded.emit()

    @property
    def is_loaded(self) -> bool:
        return self._plot_page.is_loaded

    # @staticmethod
    def _resize_event(self, event: QEvent.Type.Resize):
        # self._view.page().runJavaScript('adjustSize()')
        ...

    def _javascript_console_message(self, level, message: str, line_number: int, source_id: str):
        logging.getLogger('client.app').warning(f"{self} JS level {level}:\n"
                                                f"\t{message}\n"
                                                f"\tline {line_number}, source {source_id}.")

    def load_page(self):
        self._view.setPage(self._plot_page)
        self._view.page().javaScriptConsoleMessage = self._javascript_console_message
        self._view.resizeEvent = self._resize_event

    def update_plot(self):
        self._plot_page.update_plot()

    def set_task(self, task: Task):
        self._plot_page.reset_data()

        points: list[Point] = []
        dist = task.interval[1] - task.interval[0]
        margin = dist * self.F_PLOT_MARGIN
        margin_start = task.interval[0] - margin
        margin_dist = dist + margin * 2
        for i in range(self.F_PLOT_POINTS):
            x = margin_start + margin_dist * (i / self.F_PLOT_POINTS)
            points.append((x, task.f(x)))
        self._plot_page.set_function_plot(points)

    def set_rect(self, x0: float, x1: float, y0: float, y1: float):
        self._plot_page.set_rect(x0, x1, y0, y1)

    def set_rect_fill(self, fill: bool):
        self._plot_page.set_rect_fill(fill)

    def add_point(self, point: Point):
        self._plot_page.add_point(*point)

    def set_points(self, points: list[Point]):
        self._plot_page.set_points(points)

    def select_point(self, index: int):
        self._plot_page.select_point(index)


class PlotPage(QWebEnginePage):

    def __init__(self, controller: PlotController):
        super().__init__(controller)
        self._is_loaded = False
        self.loadStarted.connect(self._load_started)
        self.loadFinished.connect(self._load_finished)

        self.load(QUrl.fromLocalFile(PATH.PLOT_HTML))
        if STATE.DEBUG:
            self.setDevToolsPage(QWebEnginePage(self))

    def _load_started(self):
        self._is_loaded = False

    def _load_finished(self):
        self._is_loaded = True

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def reset_data(self):
        self.runJavaScript(f"resetPlotData()")

    def update_plot(self):
        self.runJavaScript(f"updatePlot()")

    def set_function_plot(self, points: list[Point]):
        self.runJavaScript(
            f"setFunctionPlot({json.dumps([p[0] for p in points])}, {json.dumps([p[1] for p in points])})")

    def set_rect(self, x0: float, x1: float, y0: float, y1: float):
        self.runJavaScript(
            f"setRect({x0}, {x1}, {y0}, {y1})"
        )

    def set_rect_fill(self, fill: bool):
        self.runJavaScript(
            f"setRectFill({'true' if fill else 'false'})"
        )

    def add_point(self, x: float, y: float):
        self.runJavaScript(
            f"addPoint({x}, {y})"
        )

    def set_points(self, points: list[Point]):
        self.runJavaScript(
            f"setPoints({json.dumps([p[0] for p in points])}, {json.dumps([p[1] for p in points])})")

    def select_point(self, index: int):
        self.runJavaScript(
            f"selectPoint({index if isinstance(index, int) else 'null'})"
        )


class DevToolsWindow(QMainWindow):

    def __init__(self, page: QWebEnginePage = None):
        super().__init__()
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self._dev_view = QWebEngineView(page)
        self.setCentralWidget(self._dev_view)
        self.resize(600, 800)

    @property
    def view(self):
        return self._dev_view
