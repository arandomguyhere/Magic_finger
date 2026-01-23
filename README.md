# WebScraper with Proxy Harvesting

A Python-based web scraping tool that automatically harvests country-specific proxies and uses advanced evasion techniques to avoid detection. This tool combines web scraping capabilities with intelligent proxy management for maximum effectiveness and anonymity.

## Features

### Core Scraping Features
- **Request Throttling**: Implements intelligent rate limiting to avoid overwhelming target servers
- **Randomized Intervals**: Uses varied delays between requests to simulate organic browsing patterns
- **User-Agent Rotation**: Cycles through different browser identifiers for each request
- **Proxy-Based IP Rotation**: Routes traffic through proxy servers to mask the originating address
- **Recursive Crawling**: Automatically discovers and crawls linked pages up to a configurable depth
- **JSON Output**: Stores scraped data in structured JSON format

### Async Browser-Based Scraping (New)
- **Pyppeteer Integration**: Uses headless Chrome/Chromium for JavaScript-rendered pages
- **Concurrent Batch Processing**: Execute multiple requests simultaneously with configurable limits
- **Automatic Retry with Exponential Backoff**: Handles failures gracefully with smart retry logic
- **Random Referrers & Resolutions**: Generates randomized referrer URLs and screen resolutions
- **Interactive Mode**: CLI interface for on-the-fly scraping sessions
- **Progress Tracking**: Real-time progress bars for batch operations

### Proxy Harvesting & Management
- **Automatic Proxy Harvesting**: Scrapes proxies from multiple free proxy provider websites
- **Country-Specific Filtering**: Filter proxies by country codes (e.g., US, UK, CA, etc.)
- **Multi-Source Harvesting**: Collects proxies from:
  - free-proxy-list.net
  - sslproxies.org
  - proxyscrape.com
  - geonode.com
- **Proxy Validation**: Tests harvested proxies to ensure they're working before use
- **🌍 Geographic Verification**: Verifies proxies actually originate from their claimed countries
  - Tests actual exit IP address
  - Confirms geographic location matches claimed country
  - Filters out mismatched/fake country proxies
  - Essential for geo-restricted content scraping
- **Auto-Refresh**: Automatically harvests new proxies when the pool falls below minimum threshold
- **Protocol Support**: Supports HTTP, HTTPS, SOCKS4, and SOCKS5 proxies

## Installation

### Local Installation

```bash
git clone https://github.com/yourusername/WebScraper.git
cd WebScraper
pip install -r requirements.txt
```

### Docker Installation

```bash
docker build -t webscraper -f Dockerfile .
```

## Usage

### Basic Usage

Run from the repository root directory:

```bash
python -m webscraper URL
```

### With Options

```bash
python -m webscraper URL --start_afresh true --max_depth 3 --delay_min 2 --delay_max 5
```

### Using Docker

```bash
docker run -d -v $(pwd):/app -w /app webscraper python -m webscraper URL
```

## Command-Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `url` | string | required | URL to start scraping from |
| `--start_afresh` | true/false | false | Clear existing data before starting |
| `--output_dir` | string | ./data | Directory to save scraped data |
| `--max_depth` | int | 2 | Maximum depth for recursive crawling |
| `--delay_min` | float | 1.0 | Minimum delay between requests (seconds) |
| `--delay_max` | float | 5.0 | Maximum delay between requests (seconds) |
| `--use_proxy` | flag | false | Enable proxy rotation |
| `--proxy_file` | string | None | Path to file containing proxy list |
| `--auto_harvest` | flag | false | Automatically harvest proxies from online sources |
| `--countries` | string | None | Comma-separated country codes (e.g., US,UK,CA) |
| `--no_validate` | flag | false | Skip proxy validation (faster but less reliable) |
| `--min_proxies` | int | 10 | Minimum proxies to maintain (triggers auto-harvest) |

## Examples

### Example 1: Basic Scraping (No Proxies)

```bash
python -m webscraper https://example.com
```

### Example 2: Scraping with Auto-Harvested Proxies

```bash
python -m webscraper https://example.com --use_proxy --auto_harvest
```

### Example 3: Scraping with Country-Specific Proxies (US Only)

```bash
python -m webscraper https://example.com --use_proxy --auto_harvest --countries US
```

### Example 4: Scraping with Multiple Countries (US, UK, Canada)

```bash
python -m webscraper https://example.com --use_proxy --auto_harvest --countries US,UK,CA
```

### Example 5: Using Existing Proxy List

```bash
python -m webscraper https://example.com --use_proxy --proxy_file proxies.txt
```

### Example 6: Deep Crawl with Auto-Harvested Proxies

```bash
python -m webscraper https://example.com --use_proxy --auto_harvest --max_depth 3 --countries US
```

### Example 7: Fast Harvesting (Skip Validation)

```bash
# Warning: May include non-working proxies
python -m webscraper https://example.com --use_proxy --auto_harvest --no_validate
```

### Example 8: Custom Delays and Proxy Settings

```bash
python -m webscraper https://example.com --use_proxy --auto_harvest --countries US,UK \
  --delay_min 2.5 --delay_max 7.5 --min_proxies 20
```

## Async Browser-Based Scraping

For JavaScript-heavy sites or when you need browser-level scraping, use the async scraper module powered by Pyppeteer.

### Async Scraper Usage

```bash
# Basic batch scraping (10 concurrent requests)
python -m webscraper.async_cli https://example.com --batch-size 10

# With proxy harvesting
python -m webscraper.async_cli https://example.com --batch-size 20 --use-proxy --auto-harvest

# With country-specific proxies
python -m webscraper.async_cli https://example.com --batch-size 20 --use-proxy --auto-harvest --countries US,UK

# High concurrency scraping
python -m webscraper.async_cli https://example.com --batch-size 50 --max-concurrent 20

# Run in visible browser mode (non-headless)
python -m webscraper.async_cli https://example.com --batch-size 5 --headful

# Interactive mode
python -m webscraper.async_cli --interactive
```

### Async CLI Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `url` | string | required | URL to scrape (not required in interactive mode) |
| `--batch-size` | int | 10 | Number of requests per batch |
| `--max-concurrent` | int | 10 | Maximum concurrent requests |
| `--max-retries` | int | 3 | Maximum retries per request |
| `--use-proxy` | flag | false | Enable proxy rotation |
| `--auto-harvest` | flag | false | Automatically harvest proxies |
| `--countries` | string | None | Comma-separated country codes (e.g., US,UK,CA) |
| `--num-referrers` | int | 100 | Number of referrers to generate |
| `--num-resolutions` | int | 50 | Number of screen resolutions to generate |
| `--headful` | flag | false | Run browser in visible mode |
| `--interactive` | flag | false | Run in interactive mode |
| `--no-progress` | flag | false | Disable progress bar |

### Programmatic Usage

```python
from webscraper import AsyncScraper, run_async_scraper

# Quick usage with convenience function
total, successful = run_async_scraper(
    url="https://example.com",
    batch_size=10,
    max_concurrent=5,
    use_proxy=True,
    auto_harvest=True
)

# Full control with AsyncScraper class
import asyncio

async def main():
    scraper = AsyncScraper(
        max_concurrent=10,
        max_retries=3,
        use_proxy=True,
        auto_harvest_proxies=True,
        harvest_countries=['US', 'UK']
    )

    # Generate random referrers and resolutions
    referrers = scraper.generate_referrers(100)
    resolutions = scraper.generate_resolutions(50)

    # Batch scrape single URL
    total, successful = await scraper.scrape_batch(
        url="https://example.com",
        batch_size=20,
        referrers=referrers,
        resolutions=resolutions
    )

    # Or scrape multiple URLs
    urls = ["https://example1.com", "https://example2.com"]
    results = await scraper.scrape_urls(urls)

    # Get statistics
    stats = scraper.get_stats()
    print(f"Success rate: {stats['success_rate']:.1f}%")

asyncio.run(main())
```

## 🌍 Geographic Verification (For Geo-Restricted Content)

When scraping geo-restricted content, you need to verify that proxies are **actually** from the countries they claim. Use the geo-verification tool:

### Windows
```cmd
REM Test and verify proxies from Russia, China, Iran
test_proxy_geo.bat RU,CN,IR

REM Use the verified proxies
python -m webscraper https://your-geo-blocked-site.com --use_proxy --proxy_file verified_proxies_simple.txt
```

### Linux/Mac
```bash
# Test and verify proxies from Russia, China, Iran
python test_proxy_geo.py RU,CN,IR

# Use the verified proxies
python -m webscraper https://your-geo-blocked-site.com --use_proxy --proxy_file verified_proxies_simple.txt
```

**What it does:**
- ✅ Tests if each proxy works
- ✅ Determines the **actual** exit IP address websites will see
- ✅ Verifies the proxy's **actual** country matches its claimed country
- ✅ Filters out fake/mismatched proxies
- ✅ Saves only geo-verified working proxies

**📖 For detailed information, see [GEO_VERIFICATION.md](GEO_VERIFICATION.md)**

## Output Format

Scraped data is saved in the `/data/` directory as JSON files. Each file is named using an MD5 hash of the URL and contains:

```json
{
  "url": "URL of the webpage",
  "content": "Raw HTML content of the webpage"
}
```

## Proxy Harvesting Details

### How It Works

1. **Harvesting Phase**: When `--auto_harvest` is enabled, the tool scrapes multiple proxy provider websites
2. **Country Filtering**: If `--countries` is specified, only proxies from those countries are collected
3. **Validation Phase**: Each harvested proxy is tested against a real endpoint (Google.com by default)
4. **Speed Ranking**: Valid proxies are sorted by response time (fastest first)
5. **Auto-Refresh**: During scraping, if proxy count falls below `--min_proxies`, new ones are automatically harvested

### Harvested Proxy Sources

- **free-proxy-list.net**: Large list of HTTP/HTTPS proxies with country info
- **sslproxies.org**: SSL/HTTPS proxies only
- **proxyscrape.com**: API-based proxy source with country filtering
- **geonode.com**: API with detailed proxy information

### Proxy File Format

If using manual proxy rotation with `--proxy_file`, create a text file with one proxy per line:

```
http://proxy1.example.com:8080
http://proxy2.example.com:8080
http://proxy3.example.com:8080
```

When using `--auto_harvest`, valid proxies are automatically saved to `harvested_proxies.txt` for reuse.

## Project Structure

```
WebScraper/
├── webscraper/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Command-line interface (sync)
│   ├── async_cli.py         # Command-line interface (async)
│   ├── scraper.py           # Core scraping logic with proxy integration
│   ├── async_scraper.py     # Async browser-based scraping with Pyppeteer
│   ├── proxy_harvester.py   # Proxy harvesting from multiple sources
│   ├── proxy_validator.py   # Proxy validation and testing
│   ├── config.py            # Configuration settings
│   ├── logger.py            # Logging utilities
│   └── utils.py             # Helper utilities
├── data/                    # Output directory for scraped data
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Dependencies

### Core Dependencies
- `requests`: HTTP library for making web requests
- `beautifulsoup4`: HTML parsing and link extraction
- `lxml`: Fast XML/HTML parser
- `fake-useragent`: User-Agent string rotation

### Async Scraping Dependencies
- `pyppeteer`: Headless Chrome/Chromium automation
- `faker`: Generate random referrers, resolutions, and other data
- `tqdm`: Progress bars for batch operations

## Important Notes

### Legal and Ethical Considerations

- **Respect robots.txt**: Always check and comply with a website's robots.txt file
- **Terms of Service**: Review and adhere to website terms of service before scraping
- **Rate Limiting**: Use appropriate delays to avoid overwhelming servers
- **Data Privacy**: Be mindful of collecting and storing personal information
- **Legal Compliance**: Ensure your use case complies with local laws and regulations

### Best Practices

1. Start with longer delays and reduce if safe
2. Test on your own websites first
3. Monitor your scraping activity
4. Handle errors gracefully
5. Use proxies responsibly

## Troubleshooting

### Common Issues

**Import Error**: Ensure all dependencies are installed
```bash
pip install -r requirements.txt
```

**Permission Denied**: Check write permissions for the output directory
```bash
chmod 755 data/
```

**Connection Timeout**: Increase timeout or check network connection

**Proxy Errors**: Verify proxy list format and availability

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is provided for educational purposes. Users are responsible for ensuring their use complies with applicable laws and website terms of service.

## Disclaimer

This tool is intended for educational and authorized testing purposes only. Users must:
- Obtain proper authorization before scraping any website
- Comply with all applicable laws and regulations
- Respect website terms of service and robots.txt
- Use the tool responsibly and ethically

The authors are not responsible for misuse of this tool.
