def fallback_excepthook(exc_type, exc_value, exc_traceback):
    import sys
    import logging
    import traceback

    logging.getLogger().exception('', exc_info=(exc_type, exc_value, exc_traceback))
    # traceback.print_exc()
    input()
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def setup_fallback_excepthook():
    import sys
    import logging

    if sys.excepthook is not sys.__excepthook__:
        logging.getLogger().warning("External excepthook already installed, aborting fallback.")
    else:
        logging.getLogger().info("Setting up fallback excepthook.")
        sys.excepthook = fallback_excepthook


class AppError(Exception):
    pass


class AppWarning(Warning):
    pass
