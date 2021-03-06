import logging
logger = logging.getLogger('agse_log')
handler = logging.StreamHandler()
formatter = logging.Formatter("[ %(asctime)s ] [ %(levelname)s ] %(message)s",
                              "%H:%M:%S %d-%m-%Y")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
