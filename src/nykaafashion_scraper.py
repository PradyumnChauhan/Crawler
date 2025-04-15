import requests
import xml.etree.ElementTree as ET
import csv
from typing import List, Dict

def get_nykaa_headers() -> Dict[str, str]:
    return {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    }

def get_nykaa_cookies() -> Dict[str, str]:
    return {
        'sessionId': 'm9ij984s5mo2crxq',
        'jarvis-id': '4c0c00c8-3127-4971-b72c-20c12f53dde5',
        'isMNLAPI': '{"name":"is_MPL_WEB_MNL_Login_True_V1","value":true}',
        'defaultPlpView': '[{"name":"DEFAULT_PLP_VIEW","value":"{\\"MSH25\\":\\"GRID\\"}"}]',
        '__cf_bm': '97Zo8fwIFF7nFmDtAn6lGcBB6A.jEzvteKZ4aC__9UU-1744729184-1.0.1.1-tRrNdz0ldVmNsYS1TNcuAAb2m1C4ZIJSg4nd6m6KPodZxYAwvd81bmbAIncD2bCZC4cSJntzVSGs0Bm_tjKVF8fqhYfRuxKxfUAL.9Ragco',
        'globalAccessToken': '{"access_token":"d56d7ae5-9ee1-426e-b842-a8e76c5b4ebc","token_type":"bearer","expires_in":1744747427467,"scope":"basic"}',
        'testVersion': 'invizbff.ranking-inviz.ab',
        'isShowPopularPicks': 'true'
    }

def fetch_sitemap(url: str) -> str:
    try:
        response = requests.get(
            url,
            headers=get_nykaa_headers(),
            cookies=get_nykaa_cookies(),
            timeout=15
        )
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url}: {str(e)}")
        return None

def parse_sitemap_index(xml_content: str) -> List[str]:
    try:
        root = ET.fromstring(xml_content)
        return [loc.text for loc in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    except ET.ParseError:
        print("Failed to parse sitemap index XML")
        return []

def parse_product_urls(xml_content: str) -> List[Dict[str, str]]:
    try:
        root = ET.fromstring(xml_content)
        products = []
        for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
            loc = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
            lastmod = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod').text
            products.append({'product_url': loc, 'lastmod': lastmod})
        return products
    except ET.ParseError:
        print("Failed to parse product sitemap XML")
        return []

def scrape_nykaafashion_products(
    sitemap_index_url: str = 'https://www.nykaafashion.com/sitemap-v2/sitemap-products-index.xml',
    output_csv: str = 'nykaafashion_products.csv',
    max_sitemaps: int = None,
    max_urls_per_sitemap: int = None
) -> List[Dict[str, str]]:
    
    print("Fetching sitemap index...")
    index_content = fetch_sitemap(sitemap_index_url)
    if not index_content:
        return []
    
    sitemap_urls = parse_sitemap_index(index_content)
    if max_sitemaps:
        sitemap_urls = sitemap_urls[:max_sitemaps]
    
    print(f"Found {len(sitemap_urls)} product sitemaps")
    
    all_products = []
    for sitemap_url in sitemap_urls:
        print(f"Processing {sitemap_url}")
        content = fetch_sitemap(sitemap_url)
        if not content:
            continue
            
        products = parse_product_urls(content)
        if max_urls_per_sitemap:
            products = products[:max_urls_per_sitemap]
            
        all_products.extend(products)
        print(f"  Added {len(products)} product URLs")
    
    # Save to CSV
    if output_csv and all_products:
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['product_url', 'lastmod']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_products)
        print(f"Saved {len(all_products)} products to {output_csv}")
    
    return all_products