# 🛍️ E-commerce Product Scraper

This Python-based web scraper extracts product data from multiple Indian e-commerce sites — **Virgio**, **Westside**, **Tatacliq**, and **Nykaa Fashion** — each using different scraping strategies tailored to the site's structure and tech stack.

---

## 🚀 Features

- 🔍 Detects Shopify sites and uses their APIs when available.
- 🗺️ Parses XML sitemap structures (including `.gz` compressed files).
- 🧠 Automatically extracts product info (URLs, images, titles, timestamps).
- 📦 Saves data in `scraped/` directory as CSV and JSON.
- 🔄 No hardcoded URLs — scrapes all sitemap links dynamically.

---

## 🧪 Installation

```bash
git clone https://github.com/yourusername/ecommerce-scraper.git
cd ecommerce-scraper

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run The Crawler
python main.py


