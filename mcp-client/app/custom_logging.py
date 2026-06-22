import logging

class ColoredFormatter(logging.Formatter):
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    YELLOW = "\033[33m"

    FORMATS = {
        logging.DEBUG: BLUE + "%(levelname)s: %(message)s" + RESET,
        logging.INFO: GREEN + "%(levelname)s: %(message)s" + RESET,
        logging.WARNING: YELLOW + "%(levelname)s: %(message)s" + RESET,
        logging.ERROR: RED + BOLD + "%(levelname)s: %(message)s" + RESET,
        logging.CRITICAL: RED + BOLD + "%(levelname)s: %(message)s" + RESET
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logger(level=logging.INFO):
    """
        Configures the root logger with the ColoredFormatter.
        Returns the root logger instance.
    """
    logger = logging.getLogger()
    
    # Avoid adding multiple handlers if setup_logger is called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(ColoredFormatter())
        logger.addHandler(handler)
        
    logger.setLevel(level)
    
    return logger