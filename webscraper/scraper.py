"""
Core WebScraper implementation with evasion techniques.
"""

import os
import json
import time
import random
import hashlib
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class WebScraper:
    """
    A web scraper with built-in evasion techniques including:
    - User-Agent rotation
    - Proxy rotation
    - Request throttling
    - Randomized delays
    """

    def __init__(
        self,
        output_dir="./data",
        start_afresh=False,
        max_depth=2,
        delay_min=1.0,
        delay_max=5.0,
        use_proxy=False,
        proxy_file=None
    ):
        """
        Initialize the WebScraper.

        Args:
            output_dir: Directory to save scraped data
            start_afresh: Clear existing data before starting
            max_depth: Maximum depth for recursive crawling
            delay_min: Minimum delay between requests (seconds)
            delay_max: Maximum delay between requests (seconds)
            use_proxy: Enable proxy rotation
            proxy_file: Path to file containing proxy list
        """
        self.output_dir = output_dir
        self.max_depth = max_depth
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.use_proxy = use_proxy
        self.visited_urls = set()
        self.session = requests.Session()

        # Initialize User-Agent rotation
        self.ua = UserAgent()

        # Initialize proxy list
        self.proxies = []
        if use_proxy and proxy_file:
            self._load_proxies(proxy_file)

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # Clear existing data if requested
        if start_afresh:
            self._clear_data()

    def _load_proxies(self, proxy_file):
        """Load proxies from file."""
        try:
            with open(proxy_file, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            print(f"Loaded {len(self.proxies)} proxies")
        except FileNotFoundError:
            print(f"Warning: Proxy file '{proxy_file}' not found. Continuing without proxies.")

    def _clear_data(self):
        """Clear existing data in output directory."""
        for filename in os.listdir(self.output_dir):
            filepath = os.path.join(self.output_dir, filename)
            if os.path.isfile(filepath) and filename.endswith('.json'):
                os.remove(filepath)
        print(f"Cleared existing data from {self.output_dir}")

    def _get_random_user_agent(self):
        """Get a random User-Agent string."""
        return self.ua.random

    def _get_random_proxy(self):
        """Get a random proxy from the list."""
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        return {
            'http': proxy,
            'https': proxy
        }

    def _random_delay(self):
        """Apply a random delay to mimic human browsing behavior."""
        delay = random.uniform(self.delay_min, self.delay_max)
        time.sleep(delay)
        return delay

    def _generate_filename(self, url):
        """Generate a unique filename for the URL."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return f"{url_hash}.json"

    def _save_data(self, url, content):
        """Save scraped data to JSON file."""
        data = {
            "url": url,
            "content": content
        }

        filename = self._generate_filename(url)
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _fetch_page(self, url):
        """
        Fetch a page with evasion techniques.

        Args:
            url: URL to fetch

        Returns:
            Response object or None if failed
        """
        headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        proxies = self._get_random_proxy() if self.use_proxy else None

        try:
            # Apply random delay before request
            delay = self._random_delay()
            print(f"  Delay: {delay:.2f}s")

            response = self.session.get(
                url,
                headers=headers,
                proxies=proxies,
                timeout=30,
                allow_redirects=True
            )

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            print(f"  Error fetching {url}: {e}")
            return None

    def _extract_links(self, url, html_content):
        """
        Extract all links from HTML content.

        Args:
            url: Base URL for resolving relative links
            html_content: HTML content to parse

        Returns:
            Set of absolute URLs
        """
        soup = BeautifulSoup(html_content, 'lxml')
        links = set()

        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(url, href)

            # Only include HTTP(S) URLs
            parsed = urlparse(absolute_url)
            if parsed.scheme in ['http', 'https']:
                links.add(absolute_url)

        return links

    def _should_crawl(self, url, base_domain):
        """
        Determine if a URL should be crawled.

        Args:
            url: URL to check
            base_domain: Base domain to restrict crawling

        Returns:
            True if URL should be crawled, False otherwise
        """
        parsed = urlparse(url)

        # Check if URL is in the same domain
        if parsed.netloc != base_domain:
            return False

        # Check if URL has already been visited
        if url in self.visited_urls:
            return False

        return True

    def _crawl(self, url, depth=0):
        """
        Recursively crawl a URL.

        Args:
            url: URL to crawl
            depth: Current depth level
        """
        if depth > self.max_depth:
            return

        if url in self.visited_urls:
            return

        self.visited_urls.add(url)

        print(f"\n[Depth {depth}] Crawling: {url}")

        # Fetch the page
        response = self._fetch_page(url)
        if not response:
            return

        # Save the content
        self._save_data(url, response.text)
        print(f"  Saved: {self._generate_filename(url)}")

        # Extract and crawl links
        if depth < self.max_depth:
            base_domain = urlparse(url).netloc
            links = self._extract_links(url, response.text)

            crawlable_links = [
                link for link in links
                if self._should_crawl(link, base_domain)
            ]

            print(f"  Found {len(links)} links, {len(crawlable_links)} crawlable")

            for link in crawlable_links:
                self._crawl(link, depth + 1)

    def scrape(self, url):
        """
        Start scraping from a given URL.

        Args:
            url: Starting URL
        """
        print("=" * 70)
        print("WebScraper - Web Scraping with Evasion Techniques")
        print("=" * 70)
        print(f"Starting URL: {url}")
        print(f"Max Depth: {self.max_depth}")
        print(f"Delay Range: {self.delay_min}s - {self.delay_max}s")
        print(f"Proxy Rotation: {'Enabled' if self.use_proxy else 'Disabled'}")
        print(f"Output Directory: {self.output_dir}")
        print("=" * 70)

        start_time = time.time()
        self._crawl(url)
        elapsed_time = time.time() - start_time

        print("\n" + "=" * 70)
        print(f"Scraping completed!")
        print(f"Total URLs visited: {len(self.visited_urls)}")
        print(f"Elapsed time: {elapsed_time:.2f}s")
        print("=" * 70)
