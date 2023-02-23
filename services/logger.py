import logging
import sys

logging.basicConfig(
    filename='logs/logs.log',
    level=logging.INFO,
    format=f"%(asctime)s %(levelname)-8s: %(filename)s %(funcName)s %(lineno)s - %(message)s")


def log_info(string):
    logging.info(string)
