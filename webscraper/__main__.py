"""
Main entry point for the WebScraper module.
"""

import argparse
import sys
from .scraper import WebScraper


def main():
    parser = argparse.ArgumentParser(
        description="WebScraper - A Python-based web scraping tool with evasion techniques"
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
        help="Enable proxy rotation (requires proxy list)"
    )
    parser.add_argument(
        "--proxy_file",
        type=str,
        help="Path to file containing proxy list (one per line)"
    )

    args = parser.parse_args()

    try:
        scraper = WebScraper(
            output_dir=args.output_dir,
            start_afresh=(args.start_afresh.lower() == "true"),
            max_depth=args.max_depth,
            delay_min=args.delay_min,
            delay_max=args.delay_max,
            use_proxy=args.use_proxy,
            proxy_file=args.proxy_file
        )

        print(f"Starting web scraping for: {args.url}")
        scraper.scrape(args.url)
        print("\nScraping completed successfully!")
        print(f"Data saved to: {args.output_dir}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
