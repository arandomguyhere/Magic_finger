"""
WebScraper - A Python-based web scraping tool with evasion techniques.

Features:
- Request throttling
- Randomized intervals between requests
- User-Agent rotation
- Proxy-based IP rotation
"""

__version__ = "1.0.0"
__author__ = "WebScraper"

from .scraper import WebScraper

__all__ = ["WebScraper"]
