import logging

from common.utils import CONST, PATH, STATE


class LOG_STATE:
    INIT = False
    LEVEL = None


def configure_logging():
    if LOG_STATE.INIT:
        logging.getLogger('meta').warning(f"Configuring logging for second time.")
    LOG_STATE.LEVEL = logging.DEBUG if STATE.DEBUG else (logging.INFO if not STATE.FROZEN else logging.WARNING)

    formatter = logging.Formatter('%(levelname)s:%(name)s: %(asctime)s : %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(PATH.get(CONST.BASE_NAME + '.log', mode='WRITE'))
    file_handler.setFormatter(formatter)

    logging.getLogger().addHandler(stream_handler)
    logging.getLogger().addHandler(file_handler)

    logging.getLogger().setLevel(LOG_STATE.LEVEL)

    logging.getLogger('meta').setLevel(LOG_STATE.LEVEL)

    LOG_STATE.INIT = True
    logging.getLogger().info(f"Configured logging.")


configure_logging()
