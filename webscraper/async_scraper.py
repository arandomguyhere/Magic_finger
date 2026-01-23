"""
Async WebScraper implementation with Pyppeteer for browser-based scraping.

This module provides async scraping capabilities using headless Chrome/Chromium
with features like:
- Concurrent batch processing with configurable limits
- User-Agent rotation
- Random referrers and screen resolutions
- Proxy support
- Automatic retry with exponential backoff
"""

import asyncio
import random
from typing import List, Tuple, Optional, Callable, Any
from urllib.parse import urlparse

from pyppeteer import launch, errors as pyppeteer_errors
from fake_useragent import UserAgent
from faker import Faker
from tqdm import tqdm

from .logger import get_logger
from .config import Config
from .proxy_harvester import ProxyHarvester

logger = get_logger(__name__)


class AsyncScraper:
    """
    Async web scraper using Pyppeteer for browser-based scraping.

    Provides batch processing with concurrency control, automatic retries,
    and request attribute rotation for evasion.
    """

    # Default proxy list URLs for auto-harvesting
    DEFAULT_PROXY_URLS = [
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        "https://raw.githubusercontent.com/im-razvan/proxy_list/main/http.txt",
        "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt",
        "https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt",
        "https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt",
    ]

    def __init__(
        self,
        max_concurrent: int = 10,
        max_retries: int = 3,
        headless: bool = True,
        use_proxy: bool = False,
        proxy_list: Optional[List[str]] = None,
        auto_harvest_proxies: bool = False,
        harvest_countries: Optional[List[str]] = None,
    ):
        """
        Initialize the AsyncScraper.

        Args:
            max_concurrent: Maximum concurrent browser pages
            max_retries: Maximum retry attempts per request
            headless: Run browser in headless mode
            use_proxy: Enable proxy rotation
            proxy_list: List of proxy URLs
            auto_harvest_proxies: Automatically harvest proxies if needed
            harvest_countries: Country codes for proxy filtering
        """
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.headless = headless
        self.use_proxy = use_proxy
        self.auto_harvest_proxies = auto_harvest_proxies
        self.harvest_countries = harvest_countries

        self.proxies: List[str] = proxy_list or []
        self.ua = UserAgent()
        self.faker = Faker()
        self.browser = None
        self.semaphore = None

        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0

    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])

    def generate_referrers(self, count: int) -> List[str]:
        """Generate random referrer URLs."""
        return [self.faker.url() for _ in range(count)]

    def generate_resolutions(self, count: int) -> List[Tuple[int, int]]:
        """Generate random screen resolutions."""
        return [
            (
                self.faker.random_int(min=800, max=1920),
                self.faker.random_int(min=600, max=1080)
            )
            for _ in range(count)
        ]

    async def harvest_proxies(self) -> List[str]:
        """
        Harvest proxies using the ProxyHarvester.

        Returns:
            List of proxy URLs
        """
        logger.info("Harvesting proxies...")
        harvester = ProxyHarvester(
            countries=self.harvest_countries,
            protocols=['http', 'https']
        )

        harvested = harvester.harvest()
        self.proxies = [p['url'] for p in harvested]

        logger.info(f"Harvested {len(self.proxies)} proxies")
        return self.proxies

    async def _launch_browser(self) -> None:
        """Launch the browser instance."""
        browser_args = [
            '--no-sandbox',
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--disable-setuid-sandbox',
            '--disable-infobars',
            '--window-position=0,0',
            '--ignore-certificate-errors',
            '--ignore-certificate-errors-spki-list',
        ]

        self.browser = await launch(
            headless=self.headless,
            args=browser_args,
            handleSIGINT=False,
            handleSIGTERM=False,
            handleSIGHUP=False,
        )
        logger.info("Browser launched")

    async def _close_browser(self) -> None:
        """Close the browser instance."""
        if self.browser:
            await self.browser.close()
            self.browser = None
            logger.info("Browser closed")

    def _get_random_proxy(self) -> Optional[str]:
        """Get a random proxy from the list."""
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    async def _make_request(
        self,
        url: str,
        request_number: int,
        referrers: List[str],
        resolutions: List[Tuple[int, int]],
        click_selector: Optional[str] = None,
        wait_for_selector: Optional[str] = None,
        custom_handler: Optional[Callable] = None,
    ) -> bool:
        """
        Make a single request with retry logic.

        Args:
            url: Target URL
            request_number: Request identifier for logging
            referrers: List of referrer URLs
            resolutions: List of screen resolutions
            click_selector: CSS selector for element to click
            wait_for_selector: CSS selector to wait for
            custom_handler: Custom async function to run on page

        Returns:
            True if successful, False otherwise
        """
        proxy = self._get_random_proxy() if self.use_proxy else None
        retries = 0

        while retries < self.max_retries:
            page = None
            try:
                page = await self.browser.newPage()

                # Set random attributes
                user_agent = self.ua.random
                referrer = random.choice(referrers) if referrers else self.faker.url()
                resolution = random.choice(resolutions) if resolutions else (1920, 1080)
                language = self.faker.language_code()
                accept_language = f"{language},{language[:2]};q=0.9"

                await page.setUserAgent(user_agent)
                await page.setExtraHTTPHeaders({
                    'Referer': referrer,
                    'Accept-Language': accept_language
                })
                await page.setViewport({
                    'width': resolution[0],
                    'height': resolution[1]
                })

                # Navigate to URL
                await page.goto(url, {'waitUntil': 'networkidle2', 'timeout': 30000})

                # Wait for selector if specified
                if wait_for_selector:
                    await page.waitForSelector(wait_for_selector, {'timeout': 10000})

                # Click element if specified
                if click_selector:
                    await page.waitForSelector(click_selector, {'timeout': 10000})
                    await page.click(click_selector)

                # Run custom handler if provided
                if custom_handler:
                    await custom_handler(page)

                logger.info(f"Request {request_number}: Success", extra={'proxy': proxy})
                return True

            except asyncio.TimeoutError as e:
                logger.warning(f"Request {request_number}: Timeout - {str(e)}")
            except pyppeteer_errors.NetworkError as e:
                logger.warning(f"Request {request_number}: Network error - {str(e)}")
            except pyppeteer_errors.PageError as e:
                logger.warning(f"Request {request_number}: Page error - {str(e)}")
            except Exception as e:
                logger.warning(f"Request {request_number}: Error - {str(e)}")
            finally:
                if page:
                    try:
                        await page.close()
                    except Exception:
                        pass

            retries += 1
            if retries < self.max_retries:
                delay = 2 ** retries
                logger.debug(f"Request {request_number}: Retrying in {delay}s...")
                await asyncio.sleep(delay)

        logger.error(f"Request {request_number}: Failed after {self.max_retries} retries")
        return False

    async def _bounded_request(
        self,
        url: str,
        request_number: int,
        referrers: List[str],
        resolutions: List[Tuple[int, int]],
        **kwargs: Any,
    ) -> bool:
        """Execute a request with semaphore-based concurrency control."""
        async with self.semaphore:
            return await self._make_request(
                url, request_number, referrers, resolutions, **kwargs
            )

    async def scrape_batch(
        self,
        url: str,
        batch_size: int,
        referrers: Optional[List[str]] = None,
        resolutions: Optional[List[Tuple[int, int]]] = None,
        show_progress: bool = True,
        **kwargs: Any,
    ) -> Tuple[int, int]:
        """
        Scrape a URL in batch with concurrent requests.

        Args:
            url: Target URL
            batch_size: Number of requests to make
            referrers: List of referrer URLs (auto-generated if None)
            resolutions: List of screen resolutions (auto-generated if None)
            show_progress: Show progress bar
            **kwargs: Additional arguments for _make_request

        Returns:
            Tuple of (total_requests, successful_requests)
        """
        if not self._validate_url(url):
            raise ValueError(f"Invalid URL: {url}")

        # Auto-harvest proxies if needed
        if self.use_proxy and self.auto_harvest_proxies and not self.proxies:
            await self.harvest_proxies()

        # Generate referrers and resolutions if not provided
        if referrers is None:
            referrers = self.generate_referrers(100)
        if resolutions is None:
            resolutions = self.generate_resolutions(50)

        # Initialize semaphore and browser
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        await self._launch_browser()

        self.total_requests = 0
        self.successful_requests = 0

        try:
            tasks = [
                self._bounded_request(
                    url, i + 1, referrers, resolutions, **kwargs
                )
                for i in range(batch_size)
            ]

            if show_progress:
                with tqdm(total=batch_size, unit='request', desc='Progress') as pbar:
                    for coro in asyncio.as_completed(tasks):
                        result = await coro
                        if result:
                            self.successful_requests += 1
                        self.total_requests += 1
                        pbar.update(1)
            else:
                results = await asyncio.gather(*tasks)
                self.total_requests = len(results)
                self.successful_requests = sum(1 for r in results if r)

            self.failed_requests = self.total_requests - self.successful_requests

            logger.info(
                f"Batch completed: {self.total_requests} total, "
                f"{self.successful_requests} successful, "
                f"{self.failed_requests} failed"
            )

        finally:
            await self._close_browser()

        return self.total_requests, self.successful_requests

    async def scrape_urls(
        self,
        urls: List[str],
        referrers: Optional[List[str]] = None,
        resolutions: Optional[List[Tuple[int, int]]] = None,
        show_progress: bool = True,
        **kwargs: Any,
    ) -> List[bool]:
        """
        Scrape multiple URLs concurrently.

        Args:
            urls: List of URLs to scrape
            referrers: List of referrer URLs
            resolutions: List of screen resolutions
            show_progress: Show progress bar
            **kwargs: Additional arguments for _make_request

        Returns:
            List of success status for each URL
        """
        # Auto-harvest proxies if needed
        if self.use_proxy and self.auto_harvest_proxies and not self.proxies:
            await self.harvest_proxies()

        # Generate referrers and resolutions if not provided
        if referrers is None:
            referrers = self.generate_referrers(100)
        if resolutions is None:
            resolutions = self.generate_resolutions(50)

        # Initialize semaphore and browser
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        await self._launch_browser()

        results = []

        try:
            tasks = [
                self._bounded_request(
                    url, i + 1, referrers, resolutions, **kwargs
                )
                for i, url in enumerate(urls)
            ]

            if show_progress:
                with tqdm(total=len(urls), unit='url', desc='Scraping') as pbar:
                    for coro in asyncio.as_completed(tasks):
                        result = await coro
                        results.append(result)
                        pbar.update(1)
            else:
                results = await asyncio.gather(*tasks)

            self.total_requests = len(results)
            self.successful_requests = sum(1 for r in results if r)
            self.failed_requests = self.total_requests - self.successful_requests

        finally:
            await self._close_browser()

        return results

    def get_stats(self) -> dict:
        """Get scraping statistics."""
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': (
                self.successful_requests / self.total_requests * 100
                if self.total_requests > 0 else 0
            ),
            'proxies_count': len(self.proxies),
        }


def run_async_scraper(
    url: str,
    batch_size: int = 10,
    max_concurrent: int = 10,
    use_proxy: bool = False,
    auto_harvest: bool = False,
    **kwargs: Any,
) -> Tuple[int, int]:
    """
    Convenience function to run async scraper.

    Args:
        url: Target URL
        batch_size: Number of requests
        max_concurrent: Maximum concurrent requests
        use_proxy: Enable proxy usage
        auto_harvest: Auto-harvest proxies
        **kwargs: Additional scraper arguments

    Returns:
        Tuple of (total_requests, successful_requests)
    """
    scraper = AsyncScraper(
        max_concurrent=max_concurrent,
        use_proxy=use_proxy,
        auto_harvest_proxies=auto_harvest,
        **kwargs
    )

    return asyncio.run(scraper.scrape_batch(url, batch_size))
