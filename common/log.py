import logging

from common.utils import STATE


class LOG_STATE:
    INIT = False
    LEVEL = None


def configure_logging():
    if LOG_STATE.INIT:
        logging.getLogger('meta').warning(f"Configuring logging for second time.")
    LOG_STATE.LEVEL = logging.DEBUG if STATE.DEBUG else logging.INFO
    logging.basicConfig(format='%(levelname)s:%(name)s: %(asctime)s : %(message)s')
    logging.getLogger().setLevel(LOG_STATE.LEVEL)
    logging.getLogger('meta').setLevel(LOG_STATE.LEVEL)

    LOG_STATE.INIT = True
    logging.getLogger().info(f"Configured logging.")


configure_logging()
