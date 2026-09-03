import os
from datetime import datetime
from typing import Optional
from colorama import Fore

LOG_DIR = os.path.expanduser("~/.ocsten/logs")

class Logger:
    def __init__(self, log_file: Optional[str] = None):
        os.makedirs(LOG_DIR, exist_ok=True)
        self.log_file = log_file or os.path.join(LOG_DIR, f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    def _write(self, level: str, message: str):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
    
    def log(self, level: str, message: str):
        levels = {'INFO': Fore.CYAN, 'SUCCESS': Fore.GREEN, 'WARNING': Fore.YELLOW, 'ERROR': Fore.RED}
        prefix = levels.get(level, Fore.WHITE)
        print(f"{prefix}{level}{Fore.RESET}: {message}")
        self._write(level, message)
    
    def info(self, msg): self.log('INFO', msg)
    def success(self, msg): self.log('SUCCESS', msg)
    def warning(self, msg): self.log('WARNING', msg)
    def error(self, msg): self.log('ERROR', msg) 
