import logging

from client.utils import STATE
import common.log


class LOG_STATE:
    INIT = False
    LEVEL = None


def configure_logging():
    if LOG_STATE.INIT:
        logging.getLogger('client.meta').warning(f"Configuring logging for second time.")
    LOG_STATE.LEVEL = logging.DEBUG if STATE.DEBUG else logging.INFO
    logging.basicConfig(format='%(levelname)s:%(name)s: %(asctime)s : %(message)s')
    logging.getLogger('client').setLevel(LOG_STATE.LEVEL)
    logging.getLogger('client.meta').setLevel(LOG_STATE.LEVEL)
    logging.getLogger('client.app').setLevel(LOG_STATE.LEVEL)

    LOG_STATE.INIT = True
    logging.getLogger('client').info(f"Configured logging.")


configure_logging()
