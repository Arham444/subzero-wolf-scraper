# Sub-Zero, Wolf, and Cove Scraper

Scrapy spider designed to crawl `subzero-wolf.com` and extract product models along with their documentation (PDFs).

[!IMPORTANT]
**US VPN REQUIRED**
The website `subzero-wolf.com` employs strict server-side geo-blocking. You should be connected to a US-based VPN or use a US proxy to run this scraper successfully. Without it, you will be redirected to an international landing page, and no data will be scraped.

## Features

- **Scope**: Covers all three brands (Sub-Zero, Wolf, Cove).
- **Discovery**: Uses `sitemap-US.xml` for reliable product discovery, bypassing complex navigation menus.
- **Extraction**: Collects model numbers, product types, thumbnails, and categorizes downloadable PDFs (User Guides, Specs, Installation Manuals).
- **Output**: JSON format.

## Installation

1. Clone this repository.
2. Install Scrapy:

```bash
pip install scrapy
```

## Usage

1. **Connect to a US VPN.**
2. Navigate to the project directory:

```bash
cd subzero_scraper
```

3. Run the spider:

```bash
scrapy crawl subzero_wolf
```
4. Ctrl+C to initiate Shutdown, and have it save what it got to output.json

The output will be saved to `output.json`.

## Data Structure

```json
{
  "model": "DW2450",
  "brand": "Cove",
  "product": "Dishwasher",
  "product_lang": "en",
  "file_urls": [
    "https://www.subzero-wolf.com/.../cv_dw_ucg.pdf"
  ],
  "type": "User and Care Guide",
  "url": "https://www.subzero-wolf.com/.../DW2450",
  "thumb": "https://www.subzero-wolf.com/.../dw2450.png",
  "source": "Cove Dishwashers",
  "domain": "subzero-wolf.com"
}
```
