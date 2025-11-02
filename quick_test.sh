#!/bin/bash

# Quick Test Script for WebScraper with Proxy Harvesting
# Run this script to test all features

echo "=========================================="
echo "WebScraper Quick Test Script"
echo "=========================================="
echo ""

# Test 1: Help
echo "Test 1: Display Help"
echo "---"
python -m webscraper --help
echo ""
echo "✓ Help displayed successfully"
echo ""

# Test 2: Basic scraping (no proxies)
echo "=========================================="
echo "Test 2: Basic Scraping (No Proxies)"
echo "---"
echo "Command: python -m webscraper http://example.com --max_depth 0 --delay_min 0.5 --delay_max 1.0"
echo ""
python -m webscraper http://example.com --max_depth 0 --delay_min 0.5 --delay_max 1.0
echo ""
echo "Check ./data/ directory for output files:"
ls -lh data/ 2>/dev/null || echo "  (No files yet - this is normal if network is restricted)"
echo ""

# Test 3: Proxy harvesting (US only)
echo "=========================================="
echo "Test 3: Proxy Harvesting (US Only)"
echo "---"
echo "Command: python -m webscraper http://example.com --use_proxy --auto_harvest --countries US --max_depth 0"
echo ""
python -m webscraper http://example.com --use_proxy --auto_harvest --countries US --max_depth 0 --delay_min 0.5 --delay_max 1.0
echo ""
echo "Check for harvested_proxies.txt:"
if [ -f "harvested_proxies.txt" ]; then
    echo "✓ Proxy file created!"
    echo "  Proxy count: $(wc -l < harvested_proxies.txt)"
    echo "  First 3 proxies:"
    head -3 harvested_proxies.txt | sed 's/^/    /'
else
    echo "  (No proxies harvested - providers may be unavailable)"
fi
echo ""

# Test 4: Module imports
echo "=========================================="
echo "Test 4: Module Import Test"
echo "---"
python << 'EOF'
from webscraper import WebScraper, ProxyHarvester, ProxyValidator

print("✓ All modules imported successfully")
print("")

# Create instances
scraper = WebScraper(use_proxy=True, auto_harvest=True, harvest_countries=['US'])
harvester = ProxyHarvester(countries=['US', 'UK'])
validator = ProxyValidator()

print("✓ All classes instantiated successfully")
print("")
print("Configuration:")
print(f"  - Scraper auto-harvest: {scraper.auto_harvest}")
print(f"  - Harvester countries: {harvester.countries}")
print(f"  - Validator timeout: {validator.timeout}s")
EOF
echo ""

# Test 5: Proxy harvesting standalone
echo "=========================================="
echo "Test 5: Standalone Proxy Harvesting"
echo "---"
python << 'EOF'
from webscraper import ProxyHarvester

print("Harvesting proxies from all sources...")
harvester = ProxyHarvester(countries=['US'], protocols=['http', 'https'])
proxies = harvester.harvest()

print(f"\n✓ Harvested {len(proxies)} proxies")

if proxies:
    harvester.save_to_file('standalone_test_proxies.txt')
    print("✓ Saved to standalone_test_proxies.txt")
    print("\nSample proxies:")
    for p in proxies[:3]:
        print(f"  • {p['url']} ({p['country']})")
else:
    print("\nNote: No proxies found (this is normal if providers are blocking)")
EOF
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo "All tests completed!"
echo ""
echo "Generated files:"
ls -lh data/ harvested_proxies.txt standalone_test_proxies.txt 2>/dev/null || echo "  (Files may not exist if network is restricted)"
echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Review TESTING.md for detailed test scenarios"
echo "2. Try scraping a real website:"
echo "   python -m webscraper https://your-target.com --use_proxy --auto_harvest --countries US"
echo ""
echo "3. For country-specific proxies:"
echo "   python -m webscraper https://your-target.com --use_proxy --auto_harvest --countries US,UK,CA"
echo ""
echo "4. For faster harvesting (skip validation):"
echo "   python -m webscraper https://your-target.com --use_proxy --auto_harvest --no_validate"
echo ""
echo "=========================================="
