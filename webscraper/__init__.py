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
"""

__version__ = "2.0.0"
__author__ = "WebScraper"

from .scraper import WebScraper
from .proxy_harvester import ProxyHarvester
from .proxy_validator import ProxyValidator

__all__ = ["WebScraper", "ProxyHarvester", "ProxyValidator"]
