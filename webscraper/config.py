"""
Configuration module for WebScraper.

Centralizes all configuration settings with environment variable support
and sensible defaults.
"""

import os
from typing import List


class Config:
    """Configuration class with environment variable support."""

    # Proxy Harvesting
    MAX_WORKERS: int = int(os.getenv('WEB_SCRAPER_MAX_WORKERS', '20'))
    TIMEOUT: int = int(os.getenv('WEB_SCRAPER_TIMEOUT', '10'))
    GEO_VERIFY_TIMEOUT: int = int(os.getenv('WEB_SCRAPER_GEO_TIMEOUT', '15'))

    # Test URLs for validation
    TEST_URLS: List[str] = os.getenv(
        'WEB_SCRAPER_TEST_URLS',
        'http://www.google.com,http://httpbin.org/ip'
    ).split(',')

    # Geo-location services
    GEO_SERVICES: List[tuple] = [
        ('http://httpbin.org/ip', 'httpbin'),
        ('http://ip-api.com/json/', 'ipapi'),
        ('http://ifconfig.me/all.json', 'ifconfig')
    ]

    # Retry settings
    MAX_RETRIES: int = int(os.getenv('WEB_SCRAPER_MAX_RETRIES', '3'))
    RETRY_BACKOFF_FACTOR: float = float(os.getenv('WEB_SCRAPER_RETRY_BACKOFF', '2.0'))
    RETRY_INITIAL_DELAY: float = float(os.getenv('WEB_SCRAPER_RETRY_DELAY', '1.0'))

    # Logging
    LOG_LEVEL: str = os.getenv('WEB_SCRAPER_LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE: str = os.getenv('WEB_SCRAPER_LOG_FILE', 'webscraper.log')
    LOG_MAX_BYTES: int = int(os.getenv('WEB_SCRAPER_LOG_MAX_BYTES', str(10 * 1024 * 1024)))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv('WEB_SCRAPER_LOG_BACKUP_COUNT', '5'))

    # Scraper defaults
    DEFAULT_OUTPUT_DIR: str = os.getenv('WEB_SCRAPER_OUTPUT_DIR', './data')
    DEFAULT_MAX_DEPTH: int = int(os.getenv('WEB_SCRAPER_MAX_DEPTH', '2'))
    DEFAULT_DELAY_MIN: float = float(os.getenv('WEB_SCRAPER_DELAY_MIN', '1.0'))
    DEFAULT_DELAY_MAX: float = float(os.getenv('WEB_SCRAPER_DELAY_MAX', '5.0'))
    DEFAULT_MIN_PROXIES: int = int(os.getenv('WEB_SCRAPER_MIN_PROXIES', '10'))

    # Harvester settings
    HARVESTER_SOURCES: List[str] = os.getenv(
        'WEB_SCRAPER_SOURCES',
        'free-proxy-list,sslproxies,proxyscrape,geonode'
    ).split(',')

    # User-Agent pool (rotate through these)
    USER_AGENTS: List[str] = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    ]

    @classmethod
    def validate(cls) -> None:
        """Validate configuration values."""
        if cls.MAX_WORKERS < 1:
            raise ValueError("MAX_WORKERS must be >= 1")
        if cls.TIMEOUT < 1:
            raise ValueError("TIMEOUT must be >= 1")
        if cls.MAX_RETRIES < 0:
            raise ValueError("MAX_RETRIES must be >= 0")
        if cls.RETRY_BACKOFF_FACTOR <= 0:
            raise ValueError("RETRY_BACKOFF_FACTOR must be > 0")

    @classmethod
    def display(cls) -> str:
        """Return a formatted string of current configuration."""
        return f"""
WebScraper Configuration:
=========================
Max Workers: {cls.MAX_WORKERS}
Timeout: {cls.TIMEOUT}s
Geo Verify Timeout: {cls.GEO_VERIFY_TIMEOUT}s
Max Retries: {cls.MAX_RETRIES}
Log Level: {cls.LOG_LEVEL}
Log File: {cls.LOG_FILE}
Test URLs: {', '.join(cls.TEST_URLS)}
Sources: {', '.join(cls.HARVESTER_SOURCES)}
"""


# Validate configuration on module import
Config.validate()
