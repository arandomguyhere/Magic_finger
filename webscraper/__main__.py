"""
Main entry point for the WebScraper module.
"""

import argparse
import sys
from .scraper import WebScraper


def main():
    parser = argparse.ArgumentParser(
        description="WebScraper - Web scraping tool with proxy harvesting and evasion techniques",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic scraping without proxies
  python -m webscraper https://example.com

  # Scraping with auto-harvested proxies
  python -m webscraper https://example.com --use_proxy --auto_harvest

  # Scraping with US-only proxies
  python -m webscraper https://example.com --use_proxy --auto_harvest --countries US

  # Scraping with multiple countries
  python -m webscraper https://example.com --use_proxy --auto_harvest --countries US,UK,CA
        """
    )
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument(
        "--start_afresh",
        type=str,
        default="false",
        choices=["true", "false"],
        help="Start fresh by clearing existing data (default: false)"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./data",
        help="Output directory for scraped data (default: ./data)"
    )
    parser.add_argument(
        "--max_depth",
        type=int,
        default=2,
        help="Maximum depth for crawling (default: 2)"
    )
    parser.add_argument(
        "--delay_min",
        type=float,
        default=1.0,
        help="Minimum delay between requests in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--delay_max",
        type=float,
        default=5.0,
        help="Maximum delay between requests in seconds (default: 5.0)"
    )
    parser.add_argument(
        "--use_proxy",
        action="store_true",
        help="Enable proxy rotation"
    )
    parser.add_argument(
        "--proxy_file",
        type=str,
        help="Path to file containing proxy list (one per line)"
    )
    parser.add_argument(
        "--auto_harvest",
        action="store_true",
        help="Automatically harvest proxies from online sources"
    )
    parser.add_argument(
        "--countries",
        type=str,
        help="Comma-separated list of country codes for proxy filtering (e.g., US,UK,CA)"
    )
    parser.add_argument(
        "--no_validate",
        action="store_true",
        help="Skip proxy validation (faster but may include non-working proxies)"
    )
    parser.add_argument(
        "--min_proxies",
        type=int,
        default=10,
        help="Minimum number of proxies to maintain (triggers auto-harvest) (default: 10)"
    )

    args = parser.parse_args()

    # Parse countries argument
    countries = None
    if args.countries:
        countries = [c.strip().upper() for c in args.countries.split(',')]

    try:
        scraper = WebScraper(
            output_dir=args.output_dir,
            start_afresh=(args.start_afresh.lower() == "true"),
            max_depth=args.max_depth,
            delay_min=args.delay_min,
            delay_max=args.delay_max,
            use_proxy=args.use_proxy,
            proxy_file=args.proxy_file,
            auto_harvest=args.auto_harvest,
            harvest_countries=countries,
            validate_proxies=not args.no_validate,
            min_proxies=args.min_proxies
        )

        print(f"\nStarting web scraping for: {args.url}\n")
        scraper.scrape(args.url)
        print("\nScraping completed successfully!")
        print(f"Data saved to: {args.output_dir}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
