"""
Proxy Validator - Tests proxies to ensure they are working.

This module validates proxies by testing them against real endpoints
and measures their response time.
"""

import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent


class ProxyValidator:
    """
    Validates proxies by testing connectivity and response time.
    """

    def __init__(self, timeout=10, test_url='http://www.google.com', max_workers=10):
        """
        Initialize the ProxyValidator.

        Args:
            timeout: Timeout for proxy test requests (seconds)
            test_url: URL to test proxies against
            max_workers: Maximum number of concurrent validation threads
        """
        self.timeout = timeout
        self.test_url = test_url
        self.max_workers = max_workers
        self.ua = UserAgent()

    def _test_proxy(self, proxy_dict):
        """
        Test a single proxy.

        Args:
            proxy_dict: Dictionary with proxy information

        Returns:
            Tuple of (proxy_dict, is_valid, response_time)
        """
        proxy_url = proxy_dict['url']
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }

        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }

        try:
            start_time = time.time()

            response = requests.get(
                self.test_url,
                proxies=proxies,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True
            )

            response_time = time.time() - start_time

            # Check if response is successful
            if response.status_code == 200:
                return (proxy_dict, True, response_time)
            else:
                return (proxy_dict, False, 0)

        except Exception:
            return (proxy_dict, False, 0)

    def validate(self, proxy_list, verbose=True):
        """
        Validate a list of proxies.

        Args:
            proxy_list: List of proxy dictionaries to validate
            verbose: Print detailed progress

        Returns:
            List of valid proxy dictionaries with response_time added
        """
        if not proxy_list:
            print("No proxies to validate.")
            return []

        print("=" * 70)
        print("Proxy Validator - Testing Proxies")
        print("=" * 70)
        print(f"Total Proxies to Test: {len(proxy_list)}")
        print(f"Test URL: {self.test_url}")
        print(f"Timeout: {self.timeout}s")
        print(f"Max Concurrent Tests: {self.max_workers}")
        print("=" * 70)
        print("\nTesting proxies...\n")

        valid_proxies = []
        tested = 0
        valid_count = 0

        # Use ThreadPoolExecutor for concurrent testing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all proxy tests
            future_to_proxy = {
                executor.submit(self._test_proxy, proxy): proxy
                for proxy in proxy_list
            }

            # Process completed tests
            for future in as_completed(future_to_proxy):
                tested += 1

                try:
                    proxy_dict, is_valid, response_time = future.result()

                    if is_valid:
                        valid_count += 1
                        proxy_dict['response_time'] = response_time
                        valid_proxies.append(proxy_dict)

                        if verbose:
                            print(f"  [{tested}/{len(proxy_list)}] ✓ {proxy_dict['url']} "
                                  f"({proxy_dict['country']}) - {response_time:.2f}s")
                    else:
                        if verbose:
                            print(f"  [{tested}/{len(proxy_list)}] ✗ {proxy_dict['url']} "
                                  f"({proxy_dict['country']}) - Failed")

                except Exception as e:
                    if verbose:
                        print(f"  [{tested}/{len(proxy_list)}] ✗ Error: {e}")

        # Sort by response time (fastest first)
        valid_proxies.sort(key=lambda x: x['response_time'])

        print("\n" + "=" * 70)
        print(f"Validation Complete!")
        print(f"Valid Proxies: {valid_count}/{len(proxy_list)} "
              f"({(valid_count/len(proxy_list)*100):.1f}%)")
        print("=" * 70)

        # Print summary by country
        if valid_proxies:
            country_counts = {}
            for proxy in valid_proxies:
                country = proxy.get('country', 'Unknown')
                country_counts[country] = country_counts.get(country, 0) + 1

            print("\nValid Proxies by Country:")
            for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {country}: {count}")

            print(f"\nFastest Proxy: {valid_proxies[0]['url']} "
                  f"({valid_proxies[0]['country']}) - {valid_proxies[0]['response_time']:.2f}s")
            print(f"Slowest Proxy: {valid_proxies[-1]['url']} "
                  f"({valid_proxies[-1]['country']}) - {valid_proxies[-1]['response_time']:.2f}s")
            print(f"Average Response Time: "
                  f"{sum(p['response_time'] for p in valid_proxies) / len(valid_proxies):.2f}s")

        return valid_proxies

    def validate_and_save(self, proxy_list, output_file='valid_proxies.txt', format='url'):
        """
        Validate proxies and save valid ones to file.

        Args:
            proxy_list: List of proxy dictionaries to validate
            output_file: Output filename
            format: Output format - 'url' or 'simple'

        Returns:
            List of valid proxies
        """
        valid_proxies = self.validate(proxy_list)

        if valid_proxies:
            with open(output_file, 'w') as f:
                for proxy in valid_proxies:
                    if format == 'url':
                        f.write(f"{proxy['url']}\n")
                    elif format == 'simple':
                        f.write(f"{proxy['ip']}:{proxy['port']}\n")

            print(f"\nSaved {len(valid_proxies)} valid proxies to {output_file}")

        return valid_proxies
