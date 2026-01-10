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
4. Ctrl+C to initiate Shutdown, and have it save what it got be outputed to output.json

The output will be saved to a timestamped file (e.g., `subzero_wolf_2023-10-27T10-30-00.json`) to prevent overwriting previous data.

### Resuming a Stopped Crawl

To start a crawler that you can pause and resume later without losing progress, use a job directory:

```bash
scrapy crawl subzero_wolf -s JOBDIR=crawls/subzero-job-1
```

If you stop the spider (Ctrl+C), running this command again will resume exactly where it left off, and new data will be appended to the existing output file if you configure it manually or merged later. Note that with timestamped files, each run creates a new file. You can simply concatenate them later: `jq -s 'add' *.json > combined.json` (Linux/Mac) or manual method (Windows).

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
