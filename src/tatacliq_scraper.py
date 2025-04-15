import gzip
import io
import xml.etree.ElementTree as ET
import csv
from src.common import get_url
from bs4 import BeautifulSoup

def get_tatacliq_sitemap_urls_from_index(sitemap_index_url="https://www.tatacliq.com/sitemap.xml"):
    """
    Fetch the main Tatacliq sitemap index and extract all sitemap URLs.
    
    Args:
        sitemap_index_url (str): URL of the main sitemap index XML.
    Returns:
        list of str: List of sitemap file URLs (typically ending with .xml.gz)
    """
    content = get_url(sitemap_index_url)
    if content is None:
        print(f"Failed to retrieve Tatacliq sitemap index from {sitemap_index_url}")
        return []
    
    # Parse the XML using ElementTree
    try:
        root = ET.fromstring(content)
    except Exception as e:
        print(f"Error parsing XML from {sitemap_index_url}: {e}")
        return []
    
    # Define the namespace for sitemap protocol
    ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = []
    
    for sitemap in root.findall("ns:sitemap", ns):
        loc_elem = sitemap.find("ns:loc", ns)
        if loc_elem is not None:
            url = loc_elem.text.strip()
            # We expect gzipped XML sitemaps; you can filter here if needed.
            if url.endswith(".xml.gz"):
                sitemap_urls.append(url)
    
    print(f"Found {len(sitemap_urls)} sitemap files from index.")
    return sitemap_urls

def extract_urls_from_gz(sitemap_url):
    """
    Downloads, decompresses, and parses a gzipped sitemap XML file.
    Extracts product-related data from each <url> element.
    
    Args:
        sitemap_url (str): URL of a gzipped sitemap.
    Returns:
        list of dict: Each dictionary contains the extracted product data.
                      Keys include 'product_url', 'image_url', 'changefreq', 'priority'
    """
    gz_data = get_url(sitemap_url)
    if gz_data is None:
        print(f"Failed to fetch data from: {sitemap_url}")
        return []

    try:
        with gzip.GzipFile(fileobj=io.BytesIO(gz_data)) as f:
            xml_data = f.read()
    except Exception as e:
        print(f"Error decompressing {sitemap_url}: {e}")
        return []
    
    try:
        root = ET.fromstring(xml_data)
    except Exception as e:
        print(f"Error parsing XML from {sitemap_url}: {e}")
        return []
    
    ns = {
        "ns": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "img": "http://www.google.com/schemas/sitemap-image/1.1"
    }
    product_data = []
    
    # Extract each <url> element.
    for url_elem in root.findall("ns:url", ns):
        loc_elem = url_elem.find("ns:loc", ns)
        image_elem = url_elem.find("img:image/img:loc", ns)
        changefreq_elem = url_elem.find("ns:changefreq", ns)
        priority_elem = url_elem.find("ns:priority", ns)
        
        loc = loc_elem.text.strip() if loc_elem is not None else ""
        image_url = image_elem.text.strip() if image_elem is not None else ""
        changefreq = changefreq_elem.text.strip() if changefreq_elem is not None else ""
        priority = priority_elem.text.strip() if priority_elem is not None else ""
        
        product_data.append({
            "product_url": loc,
            "image_url": image_url,
            "changefreq": changefreq,
            "priority": priority
        })
    
    print(f"Extracted {len(product_data)} URLs from sitemap: {sitemap_url}")
    return product_data

def scrape_tatacliq(output_csv="tatacliq_products.csv"):
    """
    Scrapes all Tatacliq product URLs by using the main sitemap index,
    fetching all sitemap files found there, and extracting product data.
    
    Args:
        output_csv (str): The CSV filename for storing the output.
    Returns:
        list of dict: Combined list of product entries from all sitemaps.
    """
    sitemap_index_url = "https://www.tatacliq.com/sitemap.xml"
    sitemap_urls = get_tatacliq_sitemap_urls_from_index(sitemap_index_url)
    all_data = []
    
    for sitemap_url in sitemap_urls:
        data = extract_urls_from_gz(sitemap_url)
        all_data.extend(data)
    
    # Remove duplicate entries based on product_url.
    unique_data = {item["product_url"]: item for item in all_data}.values()
    
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["product_url", "image_url", "changefreq", "priority"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in unique_data:
            writer.writerow(entry)
    
    print(f"Total unique product URLs saved to {output_csv}")
    return list(unique_data)

# For testing locally, you can uncomment:
# if __name__ == "__main__":
#     scrape_tatacliq()
