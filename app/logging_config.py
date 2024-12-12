import logging

logging.basicConfig(
    filename="log.log",
    filemode="w",
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.INFO,
)