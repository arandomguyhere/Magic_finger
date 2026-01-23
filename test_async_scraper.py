#!/usr/bin/env python3
"""
Test script for AsyncScraper module.

Run with: python test_async_scraper.py
"""

import asyncio
import sys


def test_imports():
    """Test that all imports work."""
    print("Testing imports...")
    from webscraper import AsyncScraper, run_async_scraper
    from webscraper.async_cli import parse_args
    print("  All imports OK")
    return True


def test_scraper_instantiation():
    """Test AsyncScraper instantiation."""
    print("Testing AsyncScraper instantiation...")
    from webscraper import AsyncScraper

    scraper = AsyncScraper(
        max_concurrent=5,
        max_retries=2,
        headless=True,
        use_proxy=False,
    )
    assert scraper.max_concurrent == 5
    assert scraper.max_retries == 2
    print("  Instantiation OK")
    return True


def test_helper_methods():
    """Test helper methods."""
    print("Testing helper methods...")
    from webscraper import AsyncScraper

    scraper = AsyncScraper()

    # Test URL validation
    assert scraper._validate_url("https://example.com") is True
    assert scraper._validate_url("not-a-url") is False
    print("  URL validation OK")

    # Test referrer generation
    refs = scraper.generate_referrers(10)
    assert len(refs) == 10
    assert all(r.startswith("http") for r in refs)
    print("  Referrer generation OK")

    # Test resolution generation
    resolutions = scraper.generate_resolutions(10)
    assert len(resolutions) == 10
    assert all(isinstance(r, tuple) and len(r) == 2 for r in resolutions)
    print("  Resolution generation OK")

    # Test proxy selection
    scraper.proxies = ["http://p1:8080", "http://p2:8080"]
    proxy = scraper._get_random_proxy()
    assert proxy in scraper.proxies
    print("  Proxy selection OK")

    return True


def test_statistics():
    """Test statistics calculation."""
    print("Testing statistics...")
    from webscraper import AsyncScraper

    scraper = AsyncScraper()
    scraper.total_requests = 100
    scraper.successful_requests = 75
    scraper.failed_requests = 25
    scraper.proxies = ["p1", "p2", "p3"]

    stats = scraper.get_stats()
    assert stats['total_requests'] == 100
    assert stats['successful_requests'] == 75
    assert stats['failed_requests'] == 25
    assert stats['success_rate'] == 75.0
    assert stats['proxies_count'] == 3
    print("  Statistics OK")
    return True


async def test_browser_launch():
    """Test browser launch (requires network for Chromium download)."""
    print("Testing browser launch...")
    from webscraper import AsyncScraper

    scraper = AsyncScraper(headless=True)

    try:
        await scraper._launch_browser()
        assert scraper.browser is not None
        print("  Browser launched OK")

        await scraper._close_browser()
        assert scraper.browser is None
        print("  Browser closed OK")
        return True
    except Exception as e:
        print(f"  Browser test failed (may need Chromium): {e}")
        return False


async def test_scrape_batch():
    """Test actual scraping (requires network)."""
    print("Testing scrape_batch...")
    from webscraper import AsyncScraper

    scraper = AsyncScraper(max_concurrent=2, max_retries=1)

    try:
        total, successful = await scraper.scrape_batch(
            "https://httpbin.org/html",
            batch_size=2,
            show_progress=False,
        )
        print(f"  Batch completed: {total} total, {successful} successful")
        return True
    except Exception as e:
        print(f"  Batch test failed (may need network): {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AsyncScraper Test Suite")
    print("=" * 60)

    results = []

    # Unit tests (no network required)
    results.append(("imports", test_imports()))
    results.append(("instantiation", test_scraper_instantiation()))
    results.append(("helper_methods", test_helper_methods()))
    results.append(("statistics", test_statistics()))

    # Integration tests (require network)
    print("\nIntegration tests (require network):")
    results.append(("browser_launch", asyncio.run(test_browser_launch())))
    results.append(("scrape_batch", asyncio.run(test_scrape_batch())))

    print("\n" + "=" * 60)
    print("Results:")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {name}: {status}")

    print(f"\nTotal: {passed}/{total} passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
