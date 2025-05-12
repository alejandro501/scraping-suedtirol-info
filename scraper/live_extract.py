import csv
import json
import time
import argparse
from pathlib import Path
from typing import Dict, Optional, List, Set

import requests
from bs4 import BeautifulSoup

from config.settings import settings
from config.languages import get_language_config
from scraper.utils import logger

class LiveSuedtirolScraper:
    def __init__(self, lang: str = "en"):
        self.lang_config = get_language_config(lang)
        self.output_file = self._prepare_output_file()
        self.processed_urls = self._load_processed_urls()

    def _prepare_output_file(self) -> Path:
        settings.output.csv_file.parent.mkdir(exist_ok=True)
        return settings.output.csv_file

    def _load_processed_urls(self) -> Set[str]:
        """Load already processed URLs from output file"""
        if not self.output_file.exists():
            return set()
        
        with self.output_file.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return {row["url"] for row in reader if "url" in row}

    def get_listing_page_url(self, page_num: int) -> str:
        """Generate URL for a specific listing page"""
        if page_num == 1:
            return settings.urls.base_url
        return f"{settings.urls.base_url}.page{page_num}"

    def extract_accommodation_urls(self, page_url: str) -> List[str]:
        """Extract accommodation URLs from a listing page"""
        try:
            response = requests.get(page_url, timeout=settings.scraper.request_timeout)
            soup = BeautifulSoup(response.text, "html.parser")
            
            urls = []
            for link in soup.find_all("a", class_=settings.urls.accommodation_class):
                if href := link.get("href"):
                    if href not in self.processed_urls:
                        urls.append(href)
            
            return urls
        except Exception as e:
            logger.error(f"Error fetching listing page {page_url}: {str(e)}")
            return []

    def get_accommodation_urls(self) -> List[str]:
        """Get all accommodation URLs from listing pages"""
        all_urls = []
        page_num = 1
        
        while True:
            page_url = self.get_listing_page_url(page_num)
            logger.info(f"Fetching listing page {page_num}")
            
            urls = self.extract_accommodation_urls(page_url)
            if not urls:
                break
                
            all_urls.extend(urls)
            
            if settings.scraper.max_pages and len(all_urls) >= settings.scraper.max_pages:
                all_urls = all_urls[:settings.scraper.max_pages]
                break
                
            page_num += 1
            time.sleep(settings.scraper.delay)
        
        logger.info(f"Found {len(all_urls)} new accommodation URLs")
        return all_urls

    def process_page(self, url: str) -> Optional[Dict]:
        """Process single accommodation page"""
        try:
            logger.debug(self.lang_config["messages"]["processing"].format(url))
            response = requests.get(url, timeout=settings.scraper.request_timeout)
            soup = BeautifulSoup(response.text, "html.parser")
            
            if script := soup.find("script", {"type": "application/ld+json"}):
                data = json.loads(script.string)
                return {
                    self.lang_config["headers"][0]: data.get("@type", ""),
                    self.lang_config["headers"][1]: data.get("name", ""),
                    self.lang_config["headers"][2]: url,
                    self.lang_config["headers"][3]: data.get("address", {}).get("addressRegion", ""),
                    self.lang_config["headers"][4]: data.get("telephone", ""),
                    self.lang_config["headers"][5]: data.get("email", ""),
                }
            logger.warning(self.lang_config["messages"]["no_data"].format(url))
            
        except Exception as e:
            logger.error(self.lang_config["messages"]["error"].format(url, str(e)))
        return None

    def run(self):
        """Main scraping workflow with chunked processing"""
        chunk_size = settings.scraper.chunk_size
        max_pages = settings.scraper.max_pages

        page_num = 1
        total_processed = 0
        emails_path = settings.output.emails_file
        emails_path.parent.mkdir(exist_ok=True)
        emails_written = set()

        with self.output_file.open("w", newline="", encoding="utf-8") as csvfile, \
             emails_path.open("w", encoding="utf-8") as emailfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.lang_config["headers"])
            writer.writeheader()

            while total_processed < max_pages:
                # Collect accommodation URLs for this chunk
                chunk_urls = []
                while len(chunk_urls) < chunk_size:
                    listing_url = self.get_listing_page_url(page_num)
                    logger.info(f"Fetching listing page {page_num}")
                    new_urls = self.extract_accommodation_urls(listing_url)
                    if not new_urls:
                        logger.info("No more URLs found. Stopping.")
                        return

                    chunk_urls.extend(new_urls)
                    page_num += 1
                    time.sleep(settings.scraper.delay)

                # Trim chunk if it would exceed max_pages
                remaining = max_pages - total_processed
                chunk_urls = chunk_urls[:remaining]

                logger.info(f"Processing chunk of {len(chunk_urls)} accommodation pages...")
                for i, url in enumerate(chunk_urls, 1):
                    if record := self.process_page(url):
                        writer.writerow(record)
                        csvfile.flush()
                        email = record.get(self.lang_config["headers"][5], "")
                        if email and email not in emails_written:
                            emailfile.write(email + "\n")
                            emails_written.add(email)
                            emailfile.flush()
                    if i < len(chunk_urls):
                        time.sleep(settings.scraper.delay)

                total_processed += len(chunk_urls)


def main():
    parser = argparse.ArgumentParser(description="Südtirol live accommodation scraper")
    parser.add_argument("--lang", choices=["en", "hu"], default="en",
                      help="Language for output (en/hu)")
    args = parser.parse_args()

    logger.info(get_language_config(args.lang)["messages"]["start"])
    scraper = LiveSuedtirolScraper(lang=args.lang)
    scraper.run()
    logger.info(get_language_config(args.lang)["messages"]["complete"])

if __name__ == "__main__":
    main()