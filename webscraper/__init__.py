"""
WebScraper - A Python-based web scraping tool with proxy harvesting and evasion techniques.

Features:
- Request throttling
- Randomized intervals between requests
- User-Agent rotation
- Proxy-based IP rotation
- Automatic proxy harvesting from multiple sources
- Country-specific proxy filtering
- Proxy validation and testing
- Async browser-based scraping with Pyppeteer
"""

__version__ = "2.1.0"
__author__ = "WebScraper"

from .scraper import WebScraper
from .proxy_harvester import ProxyHarvester
from .proxy_validator import ProxyValidator
from .async_scraper import AsyncScraper, run_async_scraper

__all__ = [
    "WebScraper",
    "ProxyHarvester",
    "ProxyValidator",
    "AsyncScraper",
    "run_async_scraper",
]
