import abc

from PySide6.QtGui import QPalette, Qt
from PySide6.QtWidgets import QWidget

from client.exceptions import AppError


class ErrorViewController(abc.ABC):

    @abc.abstractmethod
    def set_error_state(self, state: bool = True):
        ...


class ErrorWidgetController(ErrorViewController):

    def __init__(self, *widgets: QWidget):
        self._widgets = set(widgets)
        self._error = {w: False for w in self._widgets}

    def set_error_state(self, state: bool = True):
        for w in self._widgets:
            self.set_widget_state(w, state)

    def set_widget_state(self, widget: QWidget, state: bool = True):
        if widget not in self._widgets:
            raise AppError(f"{self} could not set error state on widget outside of it's control {widget}.")
        self._error[widget] = state


class ErrorPaletteController(ErrorWidgetController):
    _error_palette = QPalette()
    _error_palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.red)

    def __init__(self, *widgets: QWidget):
        super().__init__(*widgets)
        self._palettes = {w: w.palette() for w in self._widgets}

    def set_widget_state(self, widget: QWidget, state: bool = True):
        if not self._error[widget]:
            self._palettes[widget] = widget.palette()
        widget.setPalette(self._error_palette if state else self._palettes[widget])
        super().set_widget_state(widget, state)

    def error_palette(self):
        return QPalette(self._error_palette)

    def set_error_palette(self, palette: QPalette):
        for widget, state in self._error.keys():
            if state:
                widget.setPalette(palette)
        self._error_palette = QPalette(palette)
