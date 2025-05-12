import argparse
from scraper.utils import logger
from config.languages import get_language_config
from scraper.live_extract import LiveSuedtirolScraper
from scraper.sitemap_extract import SitemapScraper
# Call the startup script to check and install dependencies
from scraper.startup import ensure_dependencies

def main():
    # Ensure all dependencies are installed
    ensure_dependencies()
    parser = argparse.ArgumentParser(description="Südtirol accommodation scraper")
    parser.add_argument("--lang", choices=["en", "hu"], default="en",
                      help="Language for output (en/hu)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--live", action="store_true", help="Run only live scraping")
    group.add_argument("--sitemap", action="store_true", help="Run only sitemap scraping")
    args = parser.parse_args()

    logger.info(get_language_config(args.lang)["messages"]["start"])
    
    # Default behavior: run both (unless --live or --sitemap specified)
    if not args.live and not args.sitemap:
        logger.info("Running both live and sitemap scrapers sequentially")
        live_scraper = LiveSuedtirolScraper(lang=args.lang)
        live_scraper.run()
        
        sitemap_scraper = SitemapScraper(lang=args.lang)
        sitemap_scraper.run()
    elif args.live:
        logger.info("Running only live scraper")
        live_scraper = LiveSuedtirolScraper(lang=args.lang)
        live_scraper.run()
    elif args.sitemap:
        logger.info("Running only sitemap scraper")
        sitemap_scraper = SitemapScraper(lang=args.lang)
        sitemap_scraper.run()
    
    logger.info(get_language_config(args.lang)["messages"]["complete"])

if __name__ == "__main__":
    main()