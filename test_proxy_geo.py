#!/usr/bin/env python3
"""
Geo-Verified Proxy Testing Script

This script harvests proxies from specified countries and verifies
that they actually originate from those countries.
"""

import sys
from webscraper import ProxyHarvester, ProxyValidator


def main():
    print("=" * 70)
    print("Geo-Verified Proxy Testing")
    print("=" * 70)
    print()

    # Get countries from command line or use defaults
    if len(sys.argv) > 1:
        countries = sys.argv[1].split(',')
        countries = [c.strip().upper() for c in countries]
    else:
        countries = ['RU', 'CN', 'IR', 'UK', 'HK', 'SG']

    print(f"Target Countries: {', '.join(countries)}")
    print()

    # Step 1: Harvest proxies
    print("=" * 70)
    print("Step 1: Harvesting Proxies")
    print("=" * 70)
    print()

    harvester = ProxyHarvester(
        countries=countries,
        protocols=['http', 'https']
    )

    proxies = harvester.harvest()

    if not proxies:
        print("\nNo proxies harvested. Exiting.")
        return

    # Limit to first 50 for faster testing
    test_count = min(50, len(proxies))
    proxies_to_test = proxies[:test_count]

    print(f"\nWill test first {test_count} proxies for geo-verification...")
    print()

    # Step 2: Validate with geo-verification
    print("=" * 70)
    print("Step 2: Validating Proxies with Geographic Verification")
    print("=" * 70)
    print()
    print("This will:")
    print("  1. Test if each proxy works")
    print("  2. Determine the actual IP address seen by websites")
    print("  3. Verify the proxy's actual country matches the claimed country")
    print()

    validator = ProxyValidator(
        timeout=15,  # Longer timeout for geo lookup
        max_workers=10,
        verify_geo=True  # Enable geographic verification
    )

    valid_proxies = validator.validate(proxies_to_test, verbose=True)

    # Step 3: Summary and save results
    print()
    print("=" * 70)
    print("Results Summary")
    print("=" * 70)
    print()

    if valid_proxies:
        print(f"✓ Found {len(valid_proxies)} geo-verified working proxies")
        print()

        # Group by actual country
        by_country = {}
        for proxy in valid_proxies:
            country = proxy.get('actual_country_code', proxy.get('country', 'Unknown'))
            if country not in by_country:
                by_country[country] = []
            by_country[country].append(proxy)

        print("Proxies by Verified Country:")
        for country, country_proxies in sorted(by_country.items()):
            print(f"\n  {country}: {len(country_proxies)} proxies")
            for p in country_proxies[:3]:  # Show first 3
                ip = p.get('actual_ip', 'N/A')
                speed = p.get('response_time', 0)
                print(f"    • {p['url']} - IP: {ip} - {speed:.2f}s")
            if len(country_proxies) > 3:
                print(f"    ... and {len(country_proxies) - 3} more")

        # Save to file
        print()
        print("Saving verified proxies...")

        # Save with geo info
        with open('geo_verified_proxies.txt', 'w') as f:
            f.write("# Geo-Verified Proxies\n")
            f.write(f"# Generated for countries: {', '.join(countries)}\n")
            f.write("# Format: proxy_url | actual_country | actual_ip | response_time\n\n")

            for proxy in valid_proxies:
                url = proxy['url']
                country = proxy.get('actual_country_code', 'Unknown')
                ip = proxy.get('actual_ip', 'Unknown')
                speed = proxy.get('response_time', 0)
                f.write(f"{url} | {country} | {ip} | {speed:.2f}s\n")

        print("✓ Saved to geo_verified_proxies.txt")

        # Also save simple list for use with scraper
        with open('verified_proxies_simple.txt', 'w') as f:
            for proxy in valid_proxies:
                f.write(f"{proxy['url']}\n")

        print("✓ Saved to verified_proxies_simple.txt")

        print()
        print("=" * 70)
        print("Usage with WebScraper:")
        print("=" * 70)
        print()
        print("Now you can use these verified proxies with:")
        print()
        print("  python -m webscraper https://your-target-site.com \\")
        print("    --use_proxy \\")
        print("    --proxy_file verified_proxies_simple.txt \\")
        print("    --max_depth 2")
        print()
        print("These proxies are guaranteed to:")
        print("  ✓ Be working")
        print("  ✓ Be from the claimed country")
        print("  ✓ Show the correct exit IP to websites")
        print()

    else:
        print("✗ No valid proxies found")
        print()
        print("This can happen because:")
        print("  • Free proxies have low reliability (5-20% success rate)")
        print("  • Geographic verification is stricter (filters mismatched countries)")
        print("  • Network conditions or proxy providers may be unstable")
        print()
        print("Suggestions:")
        print("  • Try different countries: python test_proxy_geo.py US,UK,CA")
        print("  • Run the script multiple times (proxy availability changes)")
        print("  • Increase test count by editing proxies_to_test limit in script")


if __name__ == '__main__':
    main()
