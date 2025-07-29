import logging


class Logger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def log_info(self, message: str):
        self.logger.info(message)

    def log_error(self, message: str):
        self.logger.error(message)
