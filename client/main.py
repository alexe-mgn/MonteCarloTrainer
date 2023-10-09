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
            try:
                log.warning(f'Downloading Plotly JS at "{PATH.PLOTLY_JS}" with plotly lib.')
                import plotly.offline
                with open(PATH.PLOTLY_JS, mode='w', encoding='UTF-8') as f:
                    f.write(plotly.offline.get_plotlyjs())
            except:
                log.exception('')
                log.warning(f'Failed downloading Plotly JS with plotly lib, falling back to CDN download.')

                from urllib import request
                request.urlretrieve('https://cdn.plot.ly/plotly-2.25.2.min.js', PATH.PLOTLY_JS)
        except:
            log.exception(f'Failed downloading Plotly JS.')


def _test(mw):
    from client.gui.MainWindow import MainWindow
    mw: MainWindow

    cw = mw.choice_widget
    cw.inputF.setText('0.5x+1')
    cw.inputStart.setValue(0)
    cw.inputEnd.setValue(10)
    cw.inputError.setValue(0.05)
    mw.start_task()

    tw = mw.task_widget
    tw.inputRectX1.setValue(0)
    tw.inputRectX2.setValue(10)
    tw.inputRectY1.setValue(0)
    tw.inputRectY2.setValue(6)
    tw.buttonRectComplete.click()

    for _ in range(150):
        p = tw._task_session.state.points[-1]
        b = tw.buttonPointsMiss if p[1] >= tw._task_session.task.f(p[0]) else tw.buttonPointsHit
        b.click()
    tw.buttonPointsComplete.click()

    state = tw._task_session.state
    area = (state.int_x[1] - state.int_x[0]) * (state.int_y[1] - state.int_y[0])
    area_neg = (state.int_x[1] - state.int_x[0]) * max(0.0, -state.int_y[0])
    tw.inputIntResult.setValue(area * (sum(state.point_hits) / len(state.points)) - area_neg)
    tw.buttonIntComplete.click()


def run_client(task_batch_file: str | None = None, delimiter: str | None = None, test: bool = False):
    import client.log
    import logging
    try:
        from client.utils import STATE, PATH

        STATE.log_debug()
        PATH.log_debug()

        assert not ((task_batch_file is not None) and test)
        assert (task_batch_file is not None) >= (delimiter is not None)

        install()

        from PySide6.QtWidgets import QApplication
        from client.gui.MainWindow import MainWindow, DownloaderMainWindow

        app = QApplication([])

        from client.gui.ErrorDialog import ErrorDialog
        ErrorDialog.setup_excepthook()
    except:
        import traceback

        logging.getLogger('client.app').exception("")
        traceback.print_exc()
        input()
        raise

    if task_batch_file is not None:
        from common.TaskBatch import read_task_batch
        with open(task_batch_file, mode='r', encoding='utf-8') as f:
            batch = read_task_batch(f, **dict(delimiter=delimiter) if delimiter is not None else dict())
    else:
        batch = None

    if not test:
        mw = MainWindow()
        mw.choice_widget.set_task_batch(batch)
        mw.show()
    else:
        mw = DownloaderMainWindow()
        mw.choice_widget.set_task_displayed(False)
        mw.load_key_path(PATH.get('test_doc_id.txt', mode='LOAD'))
        mw.download()
        mw.show()

    if STATE.DEBUG and not test and batch is None:
        _test(mw)

    app.exec()


def run_cmd_client(*args):
    import common.exceptions
    common.exceptions.setup_fallback_excepthook()

    import argparse

    from client.utils import CONST

    parser = argparse.ArgumentParser(
        prog=CONST.CLIENT_NAME,
        description='Launch Monte Carlo method trainer client.',
    )
    f = parser.add_argument(
        '-f', '--file', type=argparse.FileType(mode='r'),
        help='Load tasks batch from .csv file so user have to choose name instead of entering task parameters.')
    d = parser.add_argument(
        '-d', '--delimiter',
        help='.csv file delimiter (-f required).')

    options = parser.parse_args(args)

    if options.delimiter is not None and options.file is None:
        raise argparse.ArgumentError(d, 'file should be specified for delimiter to have effect.')

    run_client(None if not options.file else options.file.name, delimiter=options.delimiter)


if __name__ == '__main__':
    import sys

    run_cmd_client(*sys.argv[1:])
