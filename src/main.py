import json
import csv
import os
from src.common import fix_url
from src.shopify_scraper import is_shopify, scrape_shopify_api, scrape_shopify_sitemap
from src.tatacliq_scraper import scrape_tatacliq
from src.nykaafashion_scraper import scrape_nykaafashion_products

SCRAPED_DIR = "scraped"

# Ensure the scraped folder exists
os.makedirs(SCRAPED_DIR, exist_ok=True)

def save_all_products_summary(results):
    # Save JSON
    json_path = os.path.join(SCRAPED_DIR, "all_products_summary.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
    print(f"Saved: {json_path}")

    # Save CSV
    csv_path = os.path.join(SCRAPED_DIR, "all_products_summary.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["domain", "url"])
        for domain, urls in results.items():
            for url in urls:
                writer.writerow([domain, url])
    print(f"Saved: {csv_path}")


def main():
    results = {}

    # Domain definitions.
    domains = {
        "virgio": "https://www.virgio.com",
        "nykaafashion": "https://www.nykaafashion.com",
        "westside": "https://www.westside.com",
        "tatacliq": "https://www.tatacliq.com",
    }

    for domain, url in domains.items():
        fixed_url = fix_url(url)
        print(f"\nProcessing domain: {domain} - {fixed_url}")

        if domain in ["virgio", "westside"]:
            if is_shopify(fixed_url):
                print(f"  {domain} supports Shopify API; scraping via /products.json")
                products = scrape_shopify_api(
                    fixed_url,
                    output_csv=os.path.join(SCRAPED_DIR, f"{domain}_products.csv")
                )
            else:
                print(f"  {domain} does not support /products.json; scraping via sitemap parsing")
                products = scrape_shopify_sitemap(
                    fixed_url,
                    output_csv=os.path.join(SCRAPED_DIR, f"{domain}_products_sitemap.csv")
                )
            results[domain] = products

        elif domain == "tatacliq":
            print("  Scraping Tatacliq using the main sitemap index (all sitemap files).")
            products = scrape_tatacliq(output_csv=os.path.join(SCRAPED_DIR, f"{domain}_products.csv"))
            results[domain] = products

        elif domain == "nykaafashion":
            sitemap_index_url = "https://www.nykaafashion.com/sitemap-v2/sitemap-products-index.xml"
            print("  Scraping NykaaFashion products using the sitemap index.")
            products = scrape_nykaafashion_products(
                sitemap_index_url=sitemap_index_url,
                output_csv=os.path.join(SCRAPED_DIR, "nykaafashion_products.csv"),
                max_sitemaps=None,
                max_urls_per_sitemap=None
            )
            results[domain] = products

    # Save full results
    all_json_path = os.path.join(SCRAPED_DIR, "all_products.json")
    with open(all_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
    print(f"\nAll product details saved to {all_json_path}")

    # Save summary
    save_all_products_summary(results)

if __name__ == "__main__":
    main()
