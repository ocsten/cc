import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any

MAX_RETRIES = 3
TIMEOUT_SECONDS = 30

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
    
    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        try:
            return self.session.get(url, timeout=TIMEOUT_SECONDS, **kwargs)
        except Exception:
            return None
    
    def post(self, url: str, data=None, json=None, **kwargs) -> Optional[requests.Response]:
        try:
            return self.session.post(url, data=data, json=json, timeout=TIMEOUT_SECONDS, **kwargs)
        except Exception:
            return None
    
    def close(self):
        self.session.close() 
