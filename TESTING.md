# Testing Guide for WebScraper with Proxy Harvesting

This guide will walk you through testing all features of the WebScraper tool.

## Prerequisites

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Navigate to the project directory:
```bash
cd /path/to/Magic_finger
```

## Test 1: Basic Help & Info

**Purpose**: Verify the tool is installed correctly

```bash
python -m webscraper --help
```

**Expected Output**: Help message with all available options

---

## Test 2: Basic Scraping (No Proxies)

**Purpose**: Test basic web scraping without proxy features

```bash
python -m webscraper https://example.com --max_depth 1 --delay_min 0.5 --delay_max 1.0
```

**Expected Output**:
- Tool starts scraping
- Shows progress messages
- Saves data to `./data/` directory
- Displays summary statistics

**Verify**:
```bash
ls -lh data/
cat data/*.json | head -20
```

---

## Test 3: Proxy Harvesting Only

**Purpose**: Test proxy harvesting from multiple sources

### 3a. Harvest All Countries (No Validation)

```bash
# Create a simple test script
python << 'EOF'
from webscraper.proxy_harvester import ProxyHarvester

harvester = ProxyHarvester(countries=None, protocols=['http', 'https'])
proxies = harvester.harvest()
harvester.save_to_file('test_proxies.txt', format='url')
print(f"\nHarvested {len(proxies)} proxies")
EOF
```

**Expected Output**:
- Harvesting progress from 4 sources
- Country statistics
- Proxy count summary
- Creates `test_proxies.txt` file

### 3b. Harvest US-Only Proxies

```bash
python << 'EOF'
from webscraper.proxy_harvester import ProxyHarvester

harvester = ProxyHarvester(countries=['US'], protocols=['http', 'https'])
proxies = harvester.harvest()
print(f"\nHarvested {len(proxies)} US proxies")

# Show some examples
for proxy in proxies[:5]:
    print(f"  {proxy['url']} - {proxy['country']}")
EOF
```

**Expected Output**:
- Only US proxies harvested
- Shows proxy URLs with country

### 3c. Harvest Multiple Countries

```bash
python << 'EOF'
from webscraper.proxy_harvester import ProxyHarvester

harvester = ProxyHarvester(countries=['US', 'UK', 'CA'], protocols=['http', 'https'])
proxies = harvester.harvest()
harvester.save_to_file('multi_country_proxies.txt', format='url')

# Show country breakdown
countries = {}
for p in proxies:
    country = p.get('country', 'Unknown')
    countries[country] = countries.get(country, 0) + 1

print(f"\nTotal proxies: {len(proxies)}")
print("Breakdown by country:")
for country, count in sorted(countries.items()):
    print(f"  {country}: {count}")
EOF
```

**Expected Output**:
- Proxies from US, UK, and CA only
- Country breakdown statistics

---

## Test 4: Proxy Validation

**Purpose**: Test proxy validation with concurrent testing

```bash
python << 'EOF'
from webscraper.proxy_harvester import ProxyHarvester
from webscraper.proxy_validator import ProxyValidator

# Harvest proxies
print("Step 1: Harvesting proxies...")
harvester = ProxyHarvester(countries=['US'], protocols=['http', 'https'])
proxies = harvester.harvest()

# Validate proxies
print("\nStep 2: Validating proxies...")
validator = ProxyValidator(timeout=10, max_workers=10)
valid_proxies = validator.validate(proxies[:20])  # Test first 20 only for speed

print(f"\nValidation Results:")
print(f"  Total tested: 20")
print(f"  Valid proxies: {len(valid_proxies)}")
if valid_proxies:
    print(f"  Fastest: {valid_proxies[0]['url']} ({valid_proxies[0]['response_time']:.2f}s)")
EOF
```

**Expected Output**:
- Harvesting progress
- Validation progress with ✓ and ✗ indicators
- Summary of valid vs invalid proxies
- Response time statistics

---

## Test 5: Full Scraping with Auto-Harvested Proxies

**Purpose**: Test the complete integrated solution

### 5a. With US Proxies (Validated)

```bash
python -m webscraper https://httpbin.org/html \
  --use_proxy \
  --auto_harvest \
  --countries US \
  --max_depth 0 \
  --delay_min 1 \
  --delay_max 2 \
  --min_proxies 5
```

**Expected Output**:
- Proxy harvesting phase
- Proxy validation phase
- Scraping with proxy rotation
- Summary statistics
- Creates `harvested_proxies.txt`

### 5b. Without Validation (Faster)

```bash
python -m webscraper https://httpbin.org/html \
  --use_proxy \
  --auto_harvest \
  --countries US \
  --no_validate \
  --max_depth 0 \
  --delay_min 0.5 \
  --delay_max 1
```

**Expected Output**:
- Proxy harvesting (no validation)
- Faster startup
- May encounter more failed requests

---

## Test 6: Using Pre-Harvested Proxies

**Purpose**: Test using previously harvested proxy file

```bash
# Use the file created in previous tests
python -m webscraper https://httpbin.org/ip \
  --use_proxy \
  --proxy_file harvested_proxies.txt \
  --max_depth 0 \
  --delay_min 0.5 \
  --delay_max 1
```

**Expected Output**:
- Loads proxies from file
- No harvesting phase
- Uses loaded proxies for scraping

---

## Test 7: Multiple Countries

**Purpose**: Test scraping with proxies from multiple countries

```bash
python -m webscraper https://httpbin.org/html \
  --use_proxy \
  --auto_harvest \
  --countries US,UK,CA,DE \
  --max_depth 0 \
  --delay_min 1 \
  --delay_max 2 \
  --min_proxies 10
```

**Expected Output**:
- Harvests proxies from US, UK, CA, and DE
- Shows country breakdown
- Uses mixed country proxies during scraping

---

## Test 8: Standalone Components

**Purpose**: Test individual modules separately

### Test ProxyHarvester

```bash
python << 'EOF'
from webscraper import ProxyHarvester

harvester = ProxyHarvester(countries=['US'], protocols=['http', 'https'])
proxies = harvester.harvest(sources=['free-proxy-list'])  # Test single source
print(f"Harvested {len(proxies)} proxies from free-proxy-list")
EOF
```

### Test ProxyValidator

```bash
python << 'EOF'
from webscraper import ProxyValidator

# Create sample proxies
proxies = [
    {'url': 'http://8.8.8.8:80', 'ip': '8.8.8.8', 'port': '80', 'country': 'US', 'protocol': 'http'},
]

validator = ProxyValidator(timeout=5)
valid = validator.validate(proxies, verbose=True)
print(f"Valid: {len(valid)}")
EOF
```

---

## Verification Checklist

After running tests, verify:

- [ ] Help message displays correctly
- [ ] Basic scraping creates JSON files in `data/` directory
- [ ] Proxy harvesting retrieves proxies from multiple sources
- [ ] Country filtering works (only specified countries)
- [ ] Proxy validation filters out non-working proxies
- [ ] Auto-harvest triggers when proxy count is low
- [ ] Harvested proxies saved to `harvested_proxies.txt`
- [ ] Proxy file loading works
- [ ] Error handling works (bad URLs, failed proxies, etc.)

---

## Troubleshooting

### Issue: No proxies harvested
- **Cause**: Proxy provider websites may be down or blocking requests
- **Solution**: Try different sources or run at different times

### Issue: All proxies fail validation
- **Cause**: Free proxies often have low reliability
- **Solution**: Use `--no_validate` to skip validation or increase timeout

### Issue: Slow validation
- **Cause**: Testing many proxies with network timeouts
- **Solution**: Reduce `--min_proxies` or use `--no_validate`

### Issue: Import errors
- **Cause**: Dependencies not installed
- **Solution**: Run `pip install -r requirements.txt`

---

## Performance Notes

- **Harvesting Time**: 10-30 seconds (depends on sources)
- **Validation Time**: 1-3 minutes for 50 proxies (with timeout=10s)
- **Success Rate**: Typically 5-20% of free proxies are valid
- **Recommended**: Start with `--min_proxies 5` for testing

---

## Quick Test Commands

```bash
# Quick test without proxies (fastest)
python -m webscraper https://httpbin.org/html --max_depth 0 --delay_min 0.1 --delay_max 0.3

# Quick test with proxy harvesting (medium speed)
python -m webscraper https://httpbin.org/html --use_proxy --auto_harvest --no_validate --max_depth 0 --countries US

# Full test with validation (slower but reliable)
python -m webscraper https://httpbin.org/html --use_proxy --auto_harvest --countries US --max_depth 0 --min_proxies 5
```

---

## Example Output

When you run a full test, you should see output like:

```
======================================================================
Proxy Harvester - Collecting Proxies
======================================================================
Country Filter: US
Protocol Filter: http, https
======================================================================

Harvesting from 4 source(s)...

Harvesting from free-proxy-list...
  [free-proxy-list.net] Harvested 45 proxies
Harvesting from sslproxies...
  [sslproxies.org] Harvested 23 proxies
Harvesting from proxyscrape...
  [proxyscrape.com/http] Harvested 67 proxies
Harvesting from geonode...
  [geonode.com] Harvested 112 proxies

======================================================================
Total Unique Proxies Harvested: 187
======================================================================

Proxies by Country:
  US: 187

Validating harvested proxies...
======================================================================
Proxy Validator - Testing Proxies
======================================================================
Total Proxies to Test: 187
Test URL: http://www.google.com
Timeout: 10s
Max Concurrent Tests: 20
======================================================================

Testing proxies...

  [1/187] ✓ http://12.34.56.78:8080 (US) - 1.23s
  [2/187] ✗ http://98.76.54.32:3128 (US) - Failed
  ...

======================================================================
Validation Complete!
Valid Proxies: 23/187 (12.3%)
======================================================================

Valid Proxies by Country:
  US: 23

Fastest Proxy: http://12.34.56.78:8080 (US) - 1.23s
Slowest Proxy: http://11.22.33.44:80 (US) - 8.94s
Average Response Time: 4.56s

[Auto-Harvest] Successfully added 23 valid proxies

Saved 23 proxies to harvested_proxies.txt

Starting web scraping for: https://httpbin.org/html

======================================================================
WebScraper - Web Scraping with Evasion Techniques
======================================================================
Starting URL: https://httpbin.org/html
Max Depth: 0
Delay Range: 1.0s - 2.0s
Proxy Rotation: Enabled
Active Proxies: 23
Auto-Harvest: Enabled (min: 5 proxies)
Country Filter: US
Output Directory: ./data
======================================================================

[Depth 0] Crawling: https://httpbin.org/html
  Delay: 1.45s
  Saved: abc123def456.json
  Found 5 links, 0 crawlable

======================================================================
Scraping completed!
Total URLs visited: 1
Elapsed time: 2.67s
======================================================================

Scraping completed successfully!
Data saved to: ./data
```
