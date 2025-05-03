import logging

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # ch = logging.StreamHandler()
        fh = logging.FileHandler("sqlite_clone.log")

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # logger.addHandler(ch)
        logger.addHandler(fh)

    return logger