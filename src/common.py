import requests
import time

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/35.0.1916.47 Safari/537.36'
HEADERS = {'User-Agent': USER_AGENT}

def get_url(url, retries=3, timeout=20):
    for i in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
    return None

def fix_url(url):
    """Ensure the URL is well-formed and uses https."""
    url = url.strip()
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url
    return url.rstrip('/')
