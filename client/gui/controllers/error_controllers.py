import abc

from PySide6.QtGui import QPalette, Qt, QColor
from PySide6.QtWidgets import QWidget


class ErrorViewController(abc.ABC):

    @abc.abstractmethod
    def set_error_state(self, state: bool = True):
        ...


class ErrorWidgetController(ErrorViewController):

    def __init__(self, w: QWidget):
        self._widget = w
        self._error = False

    def widget(self):
        return self._widget

    def error_state(self):
        return self._error

    def set_error_state(self, state: bool = True):
        self._error = state


class ErrorDisablerController(ErrorWidgetController):

    def set_error_state(self, state: bool = True):
        super().set_error_state(state)
        self.widget().setEnabled(not state)


class ErrorPaletteController(ErrorWidgetController):
    PALETTE_ERROR = QPalette()
    PALETTE_HINT = QPalette()
    for cr in (
            QPalette.ColorRole.Window,
            QPalette.ColorRole.Base,
            QPalette.ColorRole.AlternateBase,
            QPalette.ColorRole.Button,
    ):
        PALETTE_ERROR.setColor(cr, QColor(Qt.GlobalColor.red).lighter(150))
        PALETTE_HINT.setColor(cr, QColor(Qt.GlobalColor.green).lighter(150))

    def __init__(self, w: QWidget):
        super().__init__(w)
        self._error_palette = QPalette(self.PALETTE_ERROR)
        self._palette = self.widget().palette()

    def error_palette(self):
        return self._error_palette

    def set_error_palette(self, palette: QPalette):
        if palette is self.PALETTE_ERROR or palette is self.PALETTE_HINT:
            palette = QPalette(palette)
        self._error_palette = palette
        if self.error_state():
            self.widget().setPalette(self.error_palette())

    def widget_palette(self):
        return self._palette

    def set_widget_palette(self, palette: QPalette):
        if not self.error_state():
            self.widget().setPalette(palette)
        self._palette = self.widget().palette()

    def state_palette(self):
        return self.error_palette() if self.error_state() else self.widget_palette()

    def set_error_state(self, state: bool = True):
        if not self.error_state():
            self._palette = self.widget().palette()
        super().set_error_state(state)
        self.widget().setPalette(self.state_palette())


class ErrorPaletteDisablerController(ErrorPaletteController, ErrorDisablerController):

    def set_error_state(self, state: bool = True):
        super(self.__class__, self).set_error_state(state)
        super(self.__class__.__base__, self).set_error_state(state)


class ErrorMultiController(ErrorViewController):

    def __init__(self, *controllers: ErrorViewController):
        self._controllers: list[ErrorViewController] = list(controllers)

    def set_error_state(self, state: bool = True):
        for c in self._controllers:
            c.set_error_state(state)

    def __getitem__(self, item: int):
        return self._controllers[item]
