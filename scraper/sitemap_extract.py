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

class SitemapScraper:
    def __init__(self, lang: str = "en"):
        self.lang_config = get_language_config(lang)
        self.output_file = settings.output.csv_file
        self.emails_file = settings.output.emails_file
        self._prepare_output_files()
        self.processed_urls = self._load_processed_urls()

    def _prepare_output_files(self):
        """Ensure output directories exist"""
        self.output_file.parent.mkdir(exist_ok=True)
        self.emails_file.parent.mkdir(exist_ok=True)

    def _load_processed_urls(self) -> Set[str]:
        """Load URLs from existing CSV to avoid re-processing"""
        processed = set()
        if self.output_file.exists():
            with self.output_file.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                processed.update(row["url"] for row in reader if "url" in row)
        return processed

    def get_accommodation_urls(self) -> List[str]:
        """Get new URLs from sitemap that aren't already processed"""
        logger.info(f"Fetching sitemap from {settings.urls.sitemap}")
        response = requests.get(settings.urls.sitemap, timeout=settings.scraper.request_timeout)
        soup = BeautifulSoup(response.content, "xml")
        
        new_urls = [
            loc.text 
            for loc in soup.find_all("loc") 
            if settings.scraper.url_pattern.lower() in loc.text.lower()
            and loc.text not in self.processed_urls
        ]
        logger.info(f"Found {len(new_urls)} new URLs in sitemap")
        return new_urls

    def process_page(self, url: str) -> Optional[Dict]:
        """Process a single accommodation page if not already processed"""
        try:
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
        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}")
        return None

    def run(self):
        """Run sitemap scraping and append new results"""
        urls = self.get_accommodation_urls()
        if not urls:
            logger.info("No new URLs to process")
            return

        mode = 'a' if self.output_file.exists() else 'w'
        with self.output_file.open(mode, newline="", encoding="utf-8") as csvfile, \
             self.emails_file.open("a", encoding="utf-8") as emailfile:
            
            writer = csv.DictWriter(csvfile, fieldnames=self.lang_config["headers"])
            if mode == 'w':
                writer.writeheader()
            
            existing_emails = set()
            if self.emails_file.exists():
                existing_emails = set(self.emails_file.read_text().splitlines())
            
            new_count = 0
            for url in urls:
                if record := self.process_page(url):
                    writer.writerow(record)
                    if email := record.get(self.lang_config["headers"][5], ""):
                        if email not in existing_emails:
                            emailfile.write(email + "\n")
                            existing_emails.add(email)
                    new_count += 1
                    time.sleep(settings.scraper.delay)
            
            logger.info(f"Added {new_count} new records to files")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Südtirol sitemap accommodation scraper")
    parser.add_argument("--lang", choices=["en", "hu"], default="en",
                      help="Language for output (en/hu)")
    args = parser.parse_args()

    logger.info(get_language_config(args.lang)["messages"]["start"])
    scraper = SitemapScraper(lang=args.lang)
    scraper.run()
    logger.info(get_language_config(args.lang)["messages"]["complete"])