# WebScraper

A Python-based web scraping tool with built-in evasion techniques for conducting web crawls while circumventing detection mechanisms.

## Features

- **Request Throttling**: Implements intelligent rate limiting to avoid overwhelming target servers
- **Randomized Intervals**: Uses varied delays between requests to simulate organic browsing patterns
- **User-Agent Rotation**: Cycles through different browser identifiers for each request
- **Proxy-Based IP Rotation**: Routes traffic through proxy servers to mask the originating address
- **Recursive Crawling**: Automatically discovers and crawls linked pages up to a configurable depth
- **JSON Output**: Stores scraped data in structured JSON format

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

## Examples

### Example 1: Basic Scraping

```bash
python -m webscraper https://example.com
```

### Example 2: Deep Crawl with Fresh Start

```bash
python -m webscraper https://example.com --start_afresh true --max_depth 3
```

### Example 3: With Proxy Rotation

```bash
python -m webscraper https://example.com --use_proxy --proxy_file proxies.txt
```

### Example 4: Custom Delays

```bash
python -m webscraper https://example.com --delay_min 2.5 --delay_max 7.5
```

## Output Format

Scraped data is saved in the `/data/` directory as JSON files. Each file is named using an MD5 hash of the URL and contains:

```json
{
  "url": "URL of the webpage",
  "content": "Raw HTML content of the webpage"
}
```

## Proxy File Format

If using proxy rotation, create a text file with one proxy per line:

```
http://proxy1.example.com:8080
http://proxy2.example.com:8080
http://proxy3.example.com:8080
```

## Project Structure

```
WebScraper/
├── webscraper/
│   ├── __init__.py       # Package initialization
│   ├── __main__.py       # Command-line interface
│   └── scraper.py        # Core scraping logic
├── data/                 # Output directory for scraped data
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
└── README.md            # This file
```

## Dependencies

- `requests`: HTTP library for making web requests
- `beautifulsoup4`: HTML parsing and link extraction
- `lxml`: Fast XML/HTML parser
- `fake-useragent`: User-Agent string rotation

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
