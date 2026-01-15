import scrapy
from scrapy.spiders import SitemapSpider
import re


class SubZeroWolfSpider(SitemapSpider):
    name = "subzero_wolf"
    allowed_domains = ["subzero-wolf.com"]
    # SiteMap Index
    sitemap_urls = ["https://www.subzero-wolf.com/sitemap-US.xml"]

    sitemap_rules = [
        ("/products/", "parse_model"),
        ("/cove/", "parse_model"),
        ("/sub-zero/", "parse_model"),
        ("/wolf/", "parse_model"),
    ]

    custom_settings = {
        "FEEDS": {
            "subzero_wolf_%(time)s.json": {
                "format": "json",
                "overwrite": False,
                "indent": 2,
            },
        },
        "CONCURRENT_REQUESTS": 8,
        "DOWNLOAD_DELAY": 0.5,
    }

    def sitemap_filter(self, entries):
        for entry in entries:
            yield entry

    def start_requests(self):
        # Inject cookies to bypass server-side geo-blocking
        cookies = {
            "countryCode": "US",
            "CountryCode": "US",
            "siteRegion": "US",
            "detected_country": "US",
        }
        for url in self.sitemap_urls:
            yield scrapy.Request(url, cookies=cookies, callback=self._parse_sitemap)

    def parse_model(self, response):
        """
        Parses a product page to extract model details and downloadable documents.
        """
        brand = "Unknown"
        if "/sub-zero/" in response.url:
            brand = "Sub-Zero"
        elif "/wolf/" in response.url:
            brand = "Wolf"
        elif "/cove/" in response.url:
            brand = "Cove"

        model = self.extract_model_number(response)
        if model == "UNKNOWN":
            return

        product_type = self.extract_product_type(response)
        product_lang = self.extract_language(response)
        thumb = self.extract_thumbnail(response)

        source = "Sub-Zero, Wolf, and Cove | Kitchen Appliances that Inspire"
        pdf_elements = response.xpath(
            '//a[contains(translate(@href, "PDF", "pdf"), ".pdf") or contains(translate(., "PDF", "pdf"), "(pdf)")]'
        )

        documents = self.categorize_documents(pdf_elements, response)

        if documents:
            for doc_type, urls in documents.items():
                yield {
                    "model": model,
                    "brand": brand,
                    "product": product_type,
                    "product_lang": product_lang,
                    "file_urls": urls,
                    "type": doc_type,
                    "url": response.url,
                    "thumb": thumb,
                    "source": source,
                    "domain": "subzero-wolf.com",
                }
        else:
            yield {
                "model": model,
                "brand": brand,
                "product": product_type,
                "product_lang": product_lang,
                "file_urls": [],
                "type": "",
                "url": response.url,
                "thumb": thumb,
                "source": source,
                "domain": "subzero-wolf.com",
            }

    def extract_model_number(self, response):
        model = response.css('.model-number::text, [class*="model"]::text').get()
        if model:
            model = model.strip()
            if "model" in model.lower() or "#" in model:
                model = None
        if not model:
            title = response.css("title::text").get()
            heading = response.css("h1::text").get()
            text_to_search = (title or "") + " " + (heading or "")
            paren_match = re.search(r"\(([A-Z]+[-]?\d+[A-Z0-9/-]*)\)", text_to_search)
            if paren_match:
                model = paren_match.group(1)
            else:
                match = re.search(
                    r"\b([A-Z]{2,}[-]?\d{3,}[A-Z0-9/-]*)\b", text_to_search
                )
                if match:
                    model = match.group(1)
        if not model:
            url_match = re.search(
                r"/([A-Z]{2,}[-]?\d{3,}[A-Z0-9/-]*)$",
                response.url.rstrip("/"),
                re.IGNORECASE,
            )
            if url_match:
                model = url_match.group(1).upper()

        return model.strip() if model else "UNKNOWN"

    def extract_product_type(self, response):
        breadcrumbs = response.css(".breadcrumb ::text, nav.breadcrumb ::text").getall()
        if breadcrumbs and len(breadcrumbs) > 1:
            return breadcrumbs[-2].strip()

        heading = response.css("h1::text, h2::text").get()
        if heading:
            types = [
                "dishwasher",
                "refrigerator",
                "freezer",
                "wine",
                "range",
                "cooktop",
                "oven",
                "microwave",
                "ventilation",
                "hood",
                "warming drawer",
                "ice",
                "beverage",
                "grill",
                "module",
                "coffee",
            ]
            heading_lower = heading.lower()
            for ptype in types:
                if ptype in heading_lower:
                    return ptype.title()

        return "Unknown"

    def extract_language(self, response):
        lang = response.css("html::attr(lang)").get()
        if lang:
            return lang.split("-")[0]

        if "/es/" in response.url or "/spanish/" in response.url:
            return "es"
        if "/fr/" in response.url or "/french/" in response.url:
            return "fr"

        return "en"

    def extract_thumbnail(self, response):
        thumb = response.css(
            ".product-image img::attr(src), .main-image img::attr(src)"
        ).get()

        if not thumb:
            thumb = response.css('img[class*="product"]::attr(src)').get()

        if not thumb:
            images = response.css("img::attr(src)").getall()
            for img in images:
                if any(x in img.lower() for x in [".jpg", ".png", ".jpeg"]):
                    if "logo" not in img.lower() and "icon" not in img.lower():
                        thumb = img
                        break

        return response.urljoin(thumb) if thumb else ""

    def categorize_documents(self, pdf_elements, response):
        documents = {}

        for element in pdf_elements:
            try:
                pdf_link = element.css("::attr(href)").get()
                link_text = element.css("::text").get() or ""
            except AttributeError:
                continue

            if not pdf_link:
                continue

            full_url = response.urljoin(pdf_link)
            pdf_lower = pdf_link.lower()
            text_lower = link_text.lower()

            search_text = text_lower + " " + pdf_lower

            if "install" in search_text:
                doc_type = "Installation Guide"
            elif any(
                x in search_text
                for x in ["spec", "specification", "dimension", "sheet", "design"]
            ):
                doc_type = "Specs & Manuals"
            elif any(x in search_text for x in ["energy", "star"]):
                doc_type = "Energy Guide"
            elif "warranty" in search_text:
                doc_type = "Warranty"
            elif any(
                x in search_text
                for x in ["user", "care", "guide", "manual", "instruction", "use"]
            ):
                doc_type = "User and Care Guide"
            else:
                doc_type = "Documentation"

            if doc_type not in documents:
                documents[doc_type] = []

            if full_url not in documents[doc_type]:
                documents[doc_type].append(full_url)

        return documents
