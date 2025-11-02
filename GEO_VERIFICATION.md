# Geographic Proxy Verification

## Why Geographic Verification Matters

When scraping geo-restricted content, you need proxies that are **actually** from specific countries. Many free proxy lists are unreliable - proxies may:

- ❌ Claim to be from Russia but actually route through the US
- ❌ Show incorrect IP addresses to target websites
- ❌ Be miscategorized or outdated
- ❌ Not work for geo-blocked content

**Geographic Verification solves this** by testing each proxy's actual exit IP and country.

## How It Works

### 1. Standard Validation (Default)
```python
validator = ProxyValidator(timeout=10)
valid_proxies = validator.validate(proxies)
```

This only checks if the proxy **works** (can connect successfully).

### 2. Geo-Verified Validation (Recommended)
```python
validator = ProxyValidator(timeout=15, verify_geo=True)
valid_proxies = validator.validate(proxies)
```

This checks:
- ✅ Proxy works (connectivity test)
- ✅ Determines actual exit IP address
- ✅ Verifies actual country matches claimed country
- ✅ Filters out mismatched proxies

## Quick Start

### Windows

```cmd
# Test proxies with geo-verification
test_proxy_geo.bat

# Or specify countries
test_proxy_geo.bat RU,CN,IR
```

### Linux/Mac

```bash
# Test proxies with geo-verification
python test_proxy_geo.py

# Or specify countries
python test_proxy_geo.py RU,CN,IR,UK,HK
```

## What You'll See

### Without Geo-Verification
```
[1/50] ✓ http://12.34.56.78:8080 (RU) - 2.34s
[2/50] ✓ http://98.76.54.32:3128 (CN) - 3.45s
```
**Problem**: You don't know if these proxies are **actually** from RU/CN!

### With Geo-Verification
```
[1/50] ✓ http://12.34.56.78:8080 (RU) IP: 12.34.56.78 - 2.34s
[2/50] ✗ http://98.76.54.32:3128 Claimed: CN, Actual: US - Geo Mismatch
```
**Success**: Mismatched proxies are filtered out automatically!

## Output Files

### geo_verified_proxies.txt
Detailed information about each proxy:
```
# Geo-Verified Proxies
# Generated for countries: RU, CN, IR, UK, HK, SG
# Format: proxy_url | actual_country | actual_ip | response_time

http://12.34.56.78:8080 | RU | 12.34.56.78 | 2.34s
http://23.45.67.89:3128 | CN | 23.45.67.89 | 3.12s
http://34.56.78.90:8888 | IR | 34.56.78.90 | 4.56s
```

### verified_proxies_simple.txt
Simple list for use with webscraper:
```
http://12.34.56.78:8080
http://23.45.67.89:3128
http://34.56.78.90:8888
```

## Usage with WebScraper

After running geo-verification:

```cmd
python -m webscraper https://your-target-site.com ^
  --use_proxy ^
  --proxy_file verified_proxies_simple.txt ^
  --max_depth 2
```

Now you're **guaranteed** to be using proxies from the correct countries!

## Example: Scraping Russian News Site

```cmd
# Step 1: Get verified Russian proxies
python test_proxy_geo.py RU

# Step 2: Use them to scrape
python -m webscraper https://russian-news-site.ru ^
  --use_proxy ^
  --proxy_file verified_proxies_simple.txt ^
  --max_depth 2
```

The target website will see requests coming from **actual Russian IPs**.

## Testing Services Used

The validator uses multiple IP geolocation services:

1. **httpbin.org** - Returns exit IP address
2. **ip-api.com** - Returns IP + country information
3. **ifconfig.me** - Backup IP lookup service

If one service is down, it automatically tries the next.

## Performance Notes

### Speed
- **Without geo-verification**: ~5-10 seconds for 50 proxies
- **With geo-verification**: ~30-60 seconds for 50 proxies (slower but accurate)

### Success Rate
- **Standard validation**: 5-20% of free proxies work
- **Geo-verified validation**: 2-10% work AND match their claimed country

### Recommendations
- Test **50-100 proxies** at a time (balance between speed and results)
- Use **timeout=15** or higher for geo-verification
- Run tests **multiple times** if needed (proxy availability changes)

## Country Code Reference

Common country codes used:

| Code | Country |
|------|---------|
| US   | United States |
| UK/GB | United Kingdom |
| RU   | Russia |
| CN   | China |
| IR   | Iran |
| HK   | Hong Kong |
| SG   | Singapore |
| CA   | Canada |
| DE   | Germany |
| FR   | France |
| JP   | Japan |
| KR   | South Korea |

**Note**: UK and GB are handled interchangeably (GB is the official ISO code)

## Advanced Usage

### Python Script

```python
from webscraper import ProxyHarvester, ProxyValidator

# Harvest proxies
harvester = ProxyHarvester(countries=['RU', 'CN'], protocols=['http', 'https'])
proxies = harvester.harvest()

# Validate with geo-verification
validator = ProxyValidator(timeout=20, max_workers=10, verify_geo=True)
valid_proxies = validator.validate(proxies)

# Filter by specific country
russian_proxies = [p for p in valid_proxies if p['actual_country_code'] == 'RU']
chinese_proxies = [p for p in valid_proxies if p['actual_country_code'] == 'CN']

print(f"Russian proxies: {len(russian_proxies)}")
print(f"Chinese proxies: {len(chinese_proxies)}")

# Use the fastest Russian proxy
if russian_proxies:
    fastest = russian_proxies[0]  # Already sorted by speed
    print(f"Fastest RU proxy: {fastest['url']} - {fastest['response_time']:.2f}s")
    print(f"Exit IP: {fastest['actual_ip']}")
```

### Validate Existing Proxy List

```python
from webscraper import ProxyValidator

# Load proxies from file
proxies = []
with open('my_proxies.txt', 'r') as f:
    for line in f:
        proxy_url = line.strip()
        if proxy_url:
            # Parse proxy URL
            protocol = 'http' if proxy_url.startswith('http://') else 'https'
            ip_port = proxy_url.split('://')[-1]
            ip, port = ip_port.split(':')

            proxies.append({
                'url': proxy_url,
                'ip': ip,
                'port': port,
                'protocol': protocol,
                'country': 'Unknown'  # Will be determined
            })

# Verify geographic location
validator = ProxyValidator(timeout=15, verify_geo=True)
verified = validator.validate(proxies)

print(f"Verified: {len(verified)} / {len(proxies)}")

# Show where they're actually located
for proxy in verified:
    print(f"{proxy['url']} -> {proxy['actual_country']} ({proxy['actual_ip']})")
```

## Troubleshooting

### All proxies fail geo-verification

**Cause**: Free proxy lists often contain mismatched data

**Solution**:
- Try multiple countries: `python test_proxy_geo.py US,UK,CA,DE,FR`
- Test more proxies (edit `test_count` in script)
- Run multiple times (availability changes)

### Geo-verification is too slow

**Cause**: Each proxy requires 2 network calls (test + geo lookup)

**Solution**:
- Reduce test count to 20-30 proxies
- Increase `max_workers` to 20-30 for parallel testing
- Use faster internet connection
- Save results and reuse verified proxies

### Some verified proxies still don't work for target site

**Cause**: Target site may have additional blocking (not just geo-based)

**Solution**:
- Use longer delays: `--delay_min 3 --delay_max 6`
- Test against actual target site first
- Try proxies from multiple countries
- Some sites block known proxy IPs regardless of country

## Integration with Auto-Harvest

When using `--auto_harvest`, geo-verification is **automatically enabled**:

```cmd
python -m webscraper https://example.com ^
  --use_proxy ^
  --auto_harvest ^
  --countries RU,CN ^
  --min_proxies 5
```

This will:
1. Harvest proxies claiming to be from RU/CN
2. Validate them with geo-verification
3. Only keep proxies that are **actually** from RU/CN
4. Use them for scraping

## Benefits Summary

| Feature | Without Geo-Verification | With Geo-Verification |
|---------|-------------------------|----------------------|
| **Reliability** | Unknown - may not work | Tested and working |
| **Country Accuracy** | ❌ Claimed only | ✅ Verified actual country |
| **Exit IP Known** | ❌ No | ✅ Yes |
| **Geo-blocking** | ❌ May fail | ✅ Works for geo-content |
| **Trust Level** | Low | High |
| **Speed** | Fast validation | Slower validation |

## Conclusion

For **geo-dependent scraping**, always use geo-verification:

```bash
# Good: Verified proxies
python test_proxy_geo.py RU,CN,IR
python -m webscraper https://target.com --use_proxy --proxy_file verified_proxies_simple.txt

# Better: Auto-harvest with verification
python -m webscraper https://target.com --use_proxy --auto_harvest --countries RU,CN,IR
```

This ensures you're actually accessing content from the countries you need! 🌍
