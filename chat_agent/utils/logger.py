import logging
import os
import sys


def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # Create a file handler
    file_handler = logging.FileHandler(os.path.join("log.txt"), encoding='utf-8', mode='a')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('[%(asctime)s %(levelname)s] %(message)s', datefmt="%Y/%m/%d-%H:%M:%S"))
    # Create a stream handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter('[%(asctime)s %(levelname)s] %(message)s', datefmt="%Y/%m/%d-%H:%M:%S"))
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


logger = get_logger()