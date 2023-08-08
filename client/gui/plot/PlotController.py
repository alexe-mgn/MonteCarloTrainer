from PySide6.QtCore import QUrl, QEvent, QObject, Qt
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QMainWindow

from client.utils import STATE, PATH


class PlotController(QObject):

    def __init__(self, view: QWebEngineView):
        super().__init__()
        self._view = view
        self._plot_page = PlotPage(self)
        if STATE.DEBUG:
            self._dev_window = DevToolsWindow(self._plot_page.devToolsPage())
            self._dev_window.show()
        self.load_page()

    # @staticmethod
    def _resize_event(self, event: QEvent.Type.Resize):
        # self._view.page().runJavaScript('adjustSize()')
        ...

    def _javascript_console_message(self, level, message: str, line_number: int, source_id: str):
        print(level, message, line_number, source_id)

    def load_page(self):
        self._view.setPage(self._plot_page)
        # self._view.page().javaScriptConsoleMessage = self._javascript_console_message
        self._view.resizeEvent = self._resize_event
        # if STATE.DEBUG:
        #     self._view.setPage(self._plot_page.devToolsPage())


class PlotPage(QWebEnginePage):

    def __init__(self, controller: PlotController):
        super().__init__(controller)
        self.load(QUrl.fromLocalFile(PATH.PLOT_HTML))
        if STATE.DEBUG:
            self.setDevToolsPage(QWebEnginePage(self))


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
