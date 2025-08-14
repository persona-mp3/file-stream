import logging 


def create_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        filename="logs.log",
        format='%(name)s  %(asctime)s : %(levelname)s : %(funcName)s -> %(message)s',
        datefmt='%d/%m/%Y %I:%M:%S %p',
        level=logging.DEBUG,
    )
    return logger
