def install():
    from client.utils import STATE
    if not STATE.FROZEN:
        from client.gui.ui_utils import compile_ui

        compile_ui()


def run():
    install()

    from PySide6.QtWidgets import QApplication
    from client.gui.TaskWidget import TaskWidget

    app = QApplication([])

    mw = TaskWidget()
    mw.show()

    app.exec()


if __name__ == '__main__':
    run()
