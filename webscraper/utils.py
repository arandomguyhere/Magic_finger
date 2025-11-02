"""
Utility functions for WebScraper.

Includes retry logic, error handling helpers, and common utilities.
"""

import time
import functools
from typing import Callable, TypeVar, Any, Optional, Tuple, Type
import requests

from .config import Config
from .logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


def retry_with_backoff(
    max_retries: Optional[int] = None,
    backoff_factor: Optional[float] = None,
    initial_delay: Optional[float] = None,
    exceptions: Tuple[Type[Exception], ...] = (
        requests.exceptions.RequestException,
        ConnectionError,
        TimeoutError,
    )
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for delay between retries
        initial_delay: Initial delay in seconds
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function

    Example:
        @retry_with_backoff(max_retries=3)
        def fetch_data(url):
            return requests.get(url)
    """
    max_retries = max_retries or Config.MAX_RETRIES
    backoff_factor = backoff_factor or Config.RETRY_BACKOFF_FACTOR
    initial_delay = initial_delay or Config.RETRY_INITIAL_DELAY

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} retries: {e}"
                        )
                        raise

                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )

                    time.sleep(delay)
                    delay *= backoff_factor

            # This should never be reached, but satisfies type checker
            raise RuntimeError(f"{func.__name__} exhausted all retries")

        return wrapper

    return decorator


def safe_request(
    method: str,
    url: str,
    timeout: Optional[int] = None,
    **kwargs: Any
) -> Optional[requests.Response]:
    """
    Make a safe HTTP request with proper error handling.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: URL to request
        timeout: Request timeout in seconds
        **kwargs: Additional arguments for requests

    Returns:
        Response object or None if request failed
    """
    timeout = timeout or Config.TIMEOUT

    try:
        response = requests.request(method, url, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response

    except requests.exceptions.Timeout:
        logger.warning(f"Timeout requesting {url}")
        return None

    except requests.exceptions.ConnectionError:
        logger.warning(f"Connection error requesting {url}")
        return None

    except requests.exceptions.HTTPError as e:
        logger.warning(f"HTTP error {e.response.status_code} for {url}")
        return None

    except requests.exceptions.RequestException as e:
        logger.warning(f"Request failed for {url}: {e}")
        return None


def format_proxy_url(ip: str, port: str, protocol: str = 'http') -> str:
    """
    Format a proxy URL from components.

    Args:
        ip: IP address
        port: Port number
        protocol: Protocol (http, https, socks4, socks5)

    Returns:
        Formatted proxy URL
    """
    return f"{protocol}://{ip}:{port}"


def parse_proxy_url(proxy_url: str) -> Tuple[str, str, str]:
    """
    Parse a proxy URL into components.

    Args:
        proxy_url: Full proxy URL

    Returns:
        Tuple of (ip, port, protocol)
    """
    protocol = 'http'
    if '://' in proxy_url:
        protocol, rest = proxy_url.split('://', 1)
    else:
        rest = proxy_url

    if ':' in rest:
        ip, port = rest.split(':', 1)
    else:
        ip, port = rest, '80'

    return ip, port, protocol


def is_valid_ip(ip: str) -> bool:
    """
    Check if a string is a valid IP address.

    Args:
        ip: IP address string

    Returns:
        True if valid, False otherwise
    """
    parts = ip.split('.')
    if len(parts) != 4:
        return False

    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except (ValueError, TypeError):
        return False


def is_valid_port(port: str) -> bool:
    """
    Check if a string is a valid port number.

    Args:
        port: Port number string

    Returns:
        True if valid, False otherwise
    """
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (ValueError, TypeError):
        return False


def normalize_country_code(country_code: str) -> str:
    """
    Normalize country codes (handle UK/GB variations).

    Args:
        country_code: Country code to normalize

    Returns:
        Normalized country code
    """
    country_code = country_code.upper().strip()

    # Handle UK/GB equivalence
    if country_code == 'UK':
        return 'GB'

    return country_code


def get_country_name(country_code: str) -> str:
    """
    Get full country name from code.

    Args:
        country_code: ISO country code

    Returns:
        Full country name or code if unknown
    """
    # Simple mapping (can be expanded)
    country_names = {
        'US': 'United States',
        'GB': 'United Kingdom',
        'UK': 'United Kingdom',
        'CA': 'Canada',
        'DE': 'Germany',
        'FR': 'France',
        'RU': 'Russia',
        'CN': 'China',
        'JP': 'Japan',
        'KR': 'South Korea',
        'IN': 'India',
        'BR': 'Brazil',
        'AU': 'Australia',
        'MX': 'Mexico',
        'ES': 'Spain',
        'IT': 'Italy',
        'NL': 'Netherlands',
        'SE': 'Sweden',
        'PL': 'Poland',
        'TR': 'Turkey',
        'ID': 'Indonesia',
        'TH': 'Thailand',
        'SG': 'Singapore',
        'HK': 'Hong Kong',
        'IR': 'Iran',
        'UA': 'Ukraine',
        'CZ': 'Czech Republic',
        'AT': 'Austria',
        'CH': 'Switzerland',
        'BE': 'Belgium',
        'NO': 'Norway',
        'DK': 'Denmark',
        'FI': 'Finland',
    }

    return country_names.get(country_code.upper(), country_code)
