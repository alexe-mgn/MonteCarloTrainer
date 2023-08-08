import traceback


def install(update=False):
    import logging
    log = logging.getLogger('meta')

    from client.utils import STATE, PATH

    if not STATE.FROZEN:
        log.warning('Unbundled runtime, compiling ui.')
        from client.gui.ui_utils import compile_ui
        compile_ui()

    import os
    if not os.path.isfile(PATH.PLOTLY_JS):
        log.warning(f'Plotly JS file not found at "{PATH.PLOTLY_JS}".')

    import plotly.offline
    if not os.path.isfile(PATH.PLOTLY_JS) or update:
        log.warning(f'Downloading Plotly JS at "{PATH.PLOTLY_JS}".')
        with open(PATH.PLOTLY_JS, mode='w', encoding='UTF-8') as f:
            f.write(plotly.offline.get_plotlyjs())


def run():
    try:
        install()

        from PySide6.QtWidgets import QApplication
        from client.gui.TaskWidget import TaskWidget

        app = QApplication([])

        mw = TaskWidget()
        mw.show()

        app.exec()
    except Exception:
        traceback.print_exc()
        from client.utils import PATH
        for k in dir(PATH):
            print(f'{k}\t=\t{getattr(PATH, k)}')
        input()


if __name__ == '__main__':
    run()
