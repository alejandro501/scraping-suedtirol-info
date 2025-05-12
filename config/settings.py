import tomllib
from pathlib import Path
from pydantic import BaseModel

class ScraperConfig(BaseModel):
    max_pages: int
    request_timeout: int
    delay: float
    url_pattern: str
    chunk_size: int

class UrlsConfig(BaseModel):
    sitemap: str
    base_url: str
    accommodation_class: str

class OutputConfig(BaseModel):
    csv_file: Path
    emails_file: Path

class Settings(BaseModel):
    scraper: ScraperConfig
    urls: UrlsConfig
    output: OutputConfig

def load_settings() -> Settings:
    with open("config/config.toml", "rb") as f:
        config = tomllib.load(f)
    return Settings(**config)

settings = load_settings()