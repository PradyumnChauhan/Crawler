import json
import csv
from .common import get_url, fix_url

def is_shopify(url):
    """Check if a Shopify site can be scraped using products.json."""
    test_url = fix_url(url) + '/products.json'
    data = get_url(test_url)
    if data:
        try:
            js = json.loads(data.decode())
            return 'products' in js
        except Exception:
            return False
    return False

def scrape_shopify_api(url, output_csv='shopify_products.csv'):
    """Scrape Shopify site using its products.json endpoint."""
    url = fix_url(url)
    page = 1
    all_products = []
    while True:
        endpoint = f"{url}/products.json?page={page}"
        data = get_url(endpoint)
        if data is None:
            break
        products_data = json.loads(data.decode()).get('products', [])
        if not products_data:
            break
        for product in products_data:
            product_url = f"{url}/products/{product.get('handle')}"
            all_products.append(product_url)
        page += 1
    # Write unique URLs to CSV
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['product_url'])
        for prod in set(all_products):
            writer.writerow([prod])
    print(f"Shopify: Found {len(set(all_products))} product URLs. Saved to {output_csv}")
    return list(set(all_products))

def scrape_shopify_sitemap(url, sitemap_path='/sitemap.xml', output_csv='shopify_products_sitemap.csv'):
    """Fallback for a Shopify site that does not expose products.json.
       Parse the sitemap to extract product URLs (assuming URLs contain /products/)"""
    url = fix_url(url)
    sitemap_url = url + sitemap_path
    data = get_url(sitemap_url)
    if data is None:
        return []
    # parse XML
    import xml.etree.ElementTree as ET
    root = ET.fromstring(data)
    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    product_urls = []
    for url_elem in root.findall('ns:url', namespaces):
        loc = url_elem.find('ns:loc', namespaces).text
        # check if URL pattern fits product pages
        if '/products/' in loc:
            product_urls.append(loc)
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['product_url'])
        for prod in set(product_urls):
            writer.writerow([prod])
    print(f"Shopify (sitemap): Found {len(set(product_urls))} product URLs. Saved to {output_csv}")
    return list(set(product_urls))
