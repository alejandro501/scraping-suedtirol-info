from typing import Dict, List

LANGUAGES = {
    "en": {
        "headers": [
            "Type",
            "Name",
            "URL",
            "Region",
            "Phone",
            "Email"
        ],
        "messages": {
            "start": "Starting Südtirol accommodation scraper",
            "complete": "Scraping completed",
            "fetching_sitemap": "Fetching sitemap from {}",
            "found_urls": "Found {} new accommodation URLs",
            "processing": "Processing {}",
            "no_data": "No JSON-LD data found at {}",
            "error": "Error processing {}: {}"
        }
    },
    "hu": {
        "headers": [
            "Típus",
            "Név",
            "URL",
            "Régió",
            "Telefon",
            "Email"
        ],
        "messages": {
            "start": "Südtirol szállás adatgyűjtés indítása",
            "complete": "Adatgyűjtés befejezve",
            "fetching_sitemap": "Sitemap letöltése innen: {}",
            "found_urls": "{} új szállás URL találva",
            "processing": "Feldolgozás: {}",
            "no_data": "Nincs JSON-LD adat itt: {}",
            "error": "Hiba a feldolgozás során {}: {}"
        }
    }
}

def get_language_config(lang: str = "en") -> Dict:
    """Get language configuration for the specified language code."""
    return LANGUAGES.get(lang, LANGUAGES["en"]) 