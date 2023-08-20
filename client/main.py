import traceback


def install(update=False):
    import logging
    log = logging.getLogger('client.meta')

    from client.utils import STATE, PATH

    if not STATE.FROZEN:
        log.warning('Unbundled runtime, compiling ui.')
        from client.gui.ui_utils import compile_ui
        compile_ui()

    import os
    if not os.path.isfile(PATH.PLOTLY_JS):
        log.warning(f'Plotly JS file not found at "{PATH.PLOTLY_JS}".')

    if not os.path.isfile(PATH.PLOTLY_JS) or update:
        try:
            import plotly.offline
            log.warning(f'Downloading Plotly JS at "{PATH.PLOTLY_JS}".')
            with open(PATH.PLOTLY_JS, mode='w', encoding='UTF-8') as f:
                f.write(plotly.offline.get_plotlyjs())
        except:
            log.exception(f'Failed downloading Plotly JS.')


def run():
    import client.log
    # configure_logging()

    import logging
    try:
        from client.utils import STATE, PATH

        STATE.log_debug()
        PATH.log_debug()

        install()

        from PySide6.QtWidgets import QApplication
        from client.gui.TaskWidget import TaskWidget

        app = QApplication([])

        mw = TaskWidget()
        mw.show()

        app.exec()
    except:
        logging.getLogger('client.app').exception("")
        traceback.print_exc()
        input()
        raise


if __name__ == '__main__':
    run()
