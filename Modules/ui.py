import os
import sys
from typing import Dict
from colorama import Fore, Style

TOOL_NAME = "OCSTEN SECURE FRAMEWORK"
VERSION = "1.0.0"
AUTHOR = "ocsten"
CHANNEL = "t.me/ocsten"
GITHUB = "github.com/ocsten"

class UI:
    @staticmethod
    def clear():
        os.system('clear' if os.name == 'posix' else 'cls')
    
    @staticmethod
    def header():
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{TOOL_NAME}  v{VERSION}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}developer: {AUTHOR}  |  channel: {CHANNEL}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}github: {GITHUB}{Style.RESET_ALL}")
        print("-" * 50)
    
    @staticmethod
    def menu():
        print(f"\n{Fore.WHITE}1.  Check Card{Fore.RESET}")
        print(f"{Fore.WHITE}2.  Lookup BIN{Fore.RESET}")
        print(f"{Fore.WHITE}3.  System Info{Fore.RESET}")
        print(f"{Fore.WHITE}4.  Network Test{Fore.RESET}")
        print(f"{Fore.WHITE}5.  View Logs{Fore.RESET}")
        print(f"{Fore.WHITE}6.  Clear Screen{Fore.RESET}")
        print(f"{Fore.WHITE}7.  Exit{Fore.RESET}")
        print("-" * 50)
    
    @staticmethod
    def prompt():
        return f"{Fore.CYAN}command{Fore.RESET} > "
    
    @staticmethod
    def result(data: Dict, title: str = "Result"):
        print(f"\n{Fore.WHITE}{title}{Fore.RESET}")
        print("-" * 40)
        for key, value in data.items():
            print(f"{Fore.LIGHTBLACK_EX}{key}{Fore.RESET}: {value}")
        print("-" * 40)
    
    @staticmethod
    def progress(current: int, total: int):
        percent = (current / total) * 100 if total > 0 else 0
        bar_length = 30
        filled = int(bar_length * current // total) if total > 0 else 0
        bar = '#' * filled + '-' * (bar_length - filled)
        print(f"\rprogress: [{bar}] {percent:.0f}%", end='', flush=True) 
