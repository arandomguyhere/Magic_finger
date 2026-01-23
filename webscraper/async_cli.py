"""
CLI entry point for the async scraper module.
"""

import argparse
import asyncio
import sys
import readline
import atexit
import os

from .async_scraper import AsyncScraper
from .logger import get_logger

logger = get_logger(__name__)

HISTORY_FILE = '.async_scraper_history'
MAX_HISTORY_LENGTH = 100


def setup_readline():
    """Setup command history and auto-completion."""
    if os.path.exists(HISTORY_FILE):
        try:
            readline.read_history_file(HISTORY_FILE)
        except (FileNotFoundError, PermissionError):
            pass
    readline.set_history_length(MAX_HISTORY_LENGTH)
    atexit.register(readline.write_history_file, HISTORY_FILE)
    readline.parse_and_bind("tab: complete")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Async WebScraper - Browser-based scraping with Pyppeteer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic batch scraping
  python -m webscraper.async_cli https://example.com --batch-size 10

  # With proxy harvesting
  python -m webscraper.async_cli https://example.com --batch-size 20 --use-proxy --auto-harvest

  # Interactive mode
  python -m webscraper.async_cli --interactive

  # With custom concurrency
  python -m webscraper.async_cli https://example.com --batch-size 50 --max-concurrent 20
        """
    )

    parser.add_argument(
        "url",
        nargs='?',
        help="URL to scrape (not required in interactive mode)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of requests per batch (default: 10)"
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=10,
        help="Maximum concurrent requests (default: 10)"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retries per request (default: 3)"
    )
    parser.add_argument(
        "--use-proxy",
        action="store_true",
        help="Enable proxy rotation"
    )
    parser.add_argument(
        "--auto-harvest",
        action="store_true",
        help="Automatically harvest proxies"
    )
    parser.add_argument(
        "--countries",
        type=str,
        help="Comma-separated country codes for proxy filtering (e.g., US,UK,CA)"
    )
    parser.add_argument(
        "--num-referrers",
        type=int,
        default=100,
        help="Number of referrers to generate (default: 100)"
    )
    parser.add_argument(
        "--num-resolutions",
        type=int,
        default=50,
        help="Number of screen resolutions to generate (default: 50)"
    )
    parser.add_argument(
        "--headful",
        action="store_true",
        help="Run browser in non-headless mode (visible)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bar"
    )

    return parser.parse_args()


async def run_scraper(args):
    """Run the async scraper with provided arguments."""
    countries = None
    if args.countries:
        countries = [c.strip().upper() for c in args.countries.split(',')]

    scraper = AsyncScraper(
        max_concurrent=args.max_concurrent,
        max_retries=args.max_retries,
        headless=not args.headful,
        use_proxy=args.use_proxy,
        auto_harvest_proxies=args.auto_harvest,
        harvest_countries=countries,
    )

    referrers = scraper.generate_referrers(args.num_referrers)
    resolutions = scraper.generate_resolutions(args.num_resolutions)

    total, successful = await scraper.scrape_batch(
        args.url,
        args.batch_size,
        referrers=referrers,
        resolutions=resolutions,
        show_progress=not args.no_progress,
    )

    stats = scraper.get_stats()
    print(f"\nResults:")
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Successful: {stats['successful_requests']}")
    print(f"  Failed: {stats['failed_requests']}")
    print(f"  Success rate: {stats['success_rate']:.1f}%")

    return total, successful


def interactive_mode():
    """Run scraper in interactive mode."""
    setup_readline()

    print("=" * 70)
    print("Async WebScraper - Interactive Mode")
    print("=" * 70)

    while True:
        try:
            url = input("\nEnter URL (or 'quit' to exit): ").strip()
            if url.lower() in ('quit', 'exit', 'q'):
                break

            if not url:
                print("Please enter a valid URL")
                continue

            batch_size_str = input("Batch size [10]: ").strip()
            batch_size = int(batch_size_str) if batch_size_str else 10

            max_concurrent_str = input("Max concurrent requests [10]: ").strip()
            max_concurrent = int(max_concurrent_str) if max_concurrent_str else 10

            use_proxy = input("Use proxy rotation? (y/n) [n]: ").strip().lower() == 'y'
            auto_harvest = False
            countries = None

            if use_proxy:
                auto_harvest = input("Auto-harvest proxies? (y/n) [y]: ").strip().lower() != 'n'
                countries_input = input("Country codes (comma-separated, or empty for all): ").strip()
                if countries_input:
                    countries = [c.strip().upper() for c in countries_input.split(',')]

            num_referrers_str = input("Number of referrers [100]: ").strip()
            num_referrers = int(num_referrers_str) if num_referrers_str else 100

            num_resolutions_str = input("Number of resolutions [50]: ").strip()
            num_resolutions = int(num_resolutions_str) if num_resolutions_str else 50

            # Create scraper and run
            scraper = AsyncScraper(
                max_concurrent=max_concurrent,
                headless=True,
                use_proxy=use_proxy,
                auto_harvest_proxies=auto_harvest,
                harvest_countries=countries,
            )

            referrers = scraper.generate_referrers(num_referrers)
            resolutions = scraper.generate_resolutions(num_resolutions)

            print(f"\nStarting batch of {batch_size} requests to {url}...")

            total, successful = asyncio.run(
                scraper.scrape_batch(url, batch_size, referrers, resolutions)
            )

            stats = scraper.get_stats()
            print(f"\nResults:")
            print(f"  Total: {stats['total_requests']}")
            print(f"  Successful: {stats['successful_requests']}")
            print(f"  Failed: {stats['failed_requests']}")
            print(f"  Success rate: {stats['success_rate']:.1f}%")

            if input("\nContinue? (y/n) [y]: ").strip().lower() == 'n':
                break

        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            break
        except ValueError as e:
            print(f"Invalid input: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Error: {e}")

    print("\nGoodbye!")


def main():
    """Main entry point."""
    args = parse_args()

    if args.interactive:
        interactive_mode()
        return

    if not args.url:
        print("Error: URL is required (use --interactive for interactive mode)")
        sys.exit(1)

    try:
        asyncio.run(run_scraper(args))
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
