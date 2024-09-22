import logging
import sys
from colorama import Fore, Style, init

init(autoreset=True)

logger = logging.getLogger('bot')
logger.setLevel(logging.DEBUG)

class ColorFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: Fore.CYAN + "[%(asctime)s] [DEBUG] %(message)s" + Style.RESET_ALL,
        logging.INFO: Fore.GREEN + "[%(asctime)s] [INFO] %(message)s" + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + "[%(asctime)s] [WARNING] %(message)s" + Style.RESET_ALL,
        logging.ERROR: Fore.RED + "[%(asctime)s] [ERROR] %(message)s" + Style.RESET_ALL,
        logging.CRITICAL: Fore.RED + Style.BRIGHT + "[%(asctime)s] [CRITICAL] %(message)s" + Style.RESET_ALL,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColorFormatter())

# Add handler to your logger
logger.addHandler(console_handler)
