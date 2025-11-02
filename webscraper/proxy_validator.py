"""
Proxy Validator - Tests proxies to ensure they are working.

This module validates proxies by testing them against real endpoints,
measures their response time, and verifies their geographic location.
"""

import time
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent


class ProxyValidator:
    """
    Validates proxies by testing connectivity, response time, and geographic location.
    """

    def __init__(self, timeout=10, test_url='http://www.google.com', max_workers=10, verify_geo=False):
        """
        Initialize the ProxyValidator.

        Args:
            timeout: Timeout for proxy test requests (seconds)
            test_url: URL to test proxies against
            max_workers: Maximum number of concurrent validation threads
            verify_geo: Verify actual geographic location of proxy
        """
        self.timeout = timeout
        self.test_url = test_url
        self.max_workers = max_workers
        self.verify_geo = verify_geo
        self.ua = UserAgent()

    def _get_proxy_geo_info(self, proxy_dict):
        """
        Get the actual geographic location of a proxy by testing it.

        Args:
            proxy_dict: Dictionary with proxy information

        Returns:
            Dictionary with 'ip', 'country', 'country_code', or None if failed
        """
        proxy_url = proxy_dict['url']
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }

        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'application/json'
        }

        # Try multiple geo-location services
        test_services = [
            ('http://httpbin.org/ip', 'httpbin'),
            ('http://ip-api.com/json/', 'ipapi'),
            ('http://ifconfig.me/all.json', 'ifconfig')
        ]

        for service_url, service_type in test_services:
            try:
                response = requests.get(
                    service_url,
                    proxies=proxies,
                    headers=headers,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    data = response.json()

                    # Parse based on service type
                    if service_type == 'httpbin':
                        # httpbin only returns IP, need another call for country
                        ip = data.get('origin', '').split(',')[0].strip()
                        if ip:
                            # Get country info
                            try:
                                geo_response = requests.get(
                                    f'http://ip-api.com/json/{ip}',
                                    timeout=self.timeout
                                )
                                if geo_response.status_code == 200:
                                    geo_data = geo_response.json()
                                    return {
                                        'ip': ip,
                                        'country': geo_data.get('country', 'Unknown'),
                                        'country_code': geo_data.get('countryCode', 'Unknown')
                                    }
                            except:
                                pass
                        return {'ip': ip, 'country': 'Unknown', 'country_code': 'Unknown'}

                    elif service_type == 'ipapi':
                        return {
                            'ip': data.get('query', 'Unknown'),
                            'country': data.get('country', 'Unknown'),
                            'country_code': data.get('countryCode', 'Unknown')
                        }

                    elif service_type == 'ifconfig':
                        return {
                            'ip': data.get('ip_addr', 'Unknown'),
                            'country': 'Unknown',  # ifconfig doesn't provide country
                            'country_code': 'Unknown'
                        }

            except Exception:
                continue

        return None

    def _test_proxy(self, proxy_dict):
        """
        Test a single proxy.

        Args:
            proxy_dict: Dictionary with proxy information

        Returns:
            Tuple of (proxy_dict, is_valid, response_time, geo_match)
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
                geo_match = True
                actual_country = None

                # Verify geographic location if requested
                if self.verify_geo:
                    geo_info = self._get_proxy_geo_info(proxy_dict)
                    if geo_info:
                        actual_country = geo_info.get('country_code', 'Unknown')
                        proxy_dict['actual_country'] = geo_info.get('country', 'Unknown')
                        proxy_dict['actual_country_code'] = actual_country
                        proxy_dict['actual_ip'] = geo_info.get('ip', 'Unknown')

                        # Check if actual country matches claimed country
                        claimed_country = proxy_dict.get('country', 'Unknown')
                        # Handle country code variations (GB vs UK, etc.)
                        claimed_codes = [claimed_country,
                                       'GB' if claimed_country == 'UK' else claimed_country,
                                       'UK' if claimed_country == 'GB' else claimed_country]

                        geo_match = actual_country in claimed_codes
                    else:
                        geo_match = False

                return (proxy_dict, True, response_time, geo_match)
            else:
                return (proxy_dict, False, 0, False)

        except Exception:
            return (proxy_dict, False, 0, False)

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
        print(f"Geographic Verification: {'Enabled' if self.verify_geo else 'Disabled'}")
        print("=" * 70)
        print("\nTesting proxies...\n")

        valid_proxies = []
        tested = 0
        valid_count = 0
        geo_mismatch_count = 0

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
                    proxy_dict, is_valid, response_time, geo_match = future.result()

                    if is_valid:
                        # Only count as valid if geo matches (when verification is enabled)
                        if self.verify_geo and not geo_match:
                            geo_mismatch_count += 1
                            if verbose:
                                claimed = proxy_dict.get('country', 'Unknown')
                                actual = proxy_dict.get('actual_country_code', 'Unknown')
                                print(f"  [{tested}/{len(proxy_list)}] ✗ {proxy_dict['url']} "
                                      f"Claimed: {claimed}, Actual: {actual} - Geo Mismatch")
                        else:
                            valid_count += 1
                            proxy_dict['response_time'] = response_time
                            valid_proxies.append(proxy_dict)

                            if verbose:
                                if self.verify_geo:
                                    actual_country = proxy_dict.get('actual_country_code', proxy_dict['country'])
                                    actual_ip = proxy_dict.get('actual_ip', 'N/A')
                                    print(f"  [{tested}/{len(proxy_list)}] ✓ {proxy_dict['url']} "
                                          f"({actual_country}) IP: {actual_ip} - {response_time:.2f}s")
                                else:
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
        if self.verify_geo and geo_mismatch_count > 0:
            print(f"Geo Mismatches: {geo_mismatch_count} (proxies claiming wrong country)")
        print("=" * 70)

        # Print summary by country
        if valid_proxies:
            country_counts = {}
            for proxy in valid_proxies:
                # Use actual country if available (when geo verification is enabled)
                if self.verify_geo and 'actual_country_code' in proxy:
                    country = proxy.get('actual_country_code', 'Unknown')
                else:
                    country = proxy.get('country', 'Unknown')
                country_counts[country] = country_counts.get(country, 0) + 1

            print(f"\n{'Verified' if self.verify_geo else 'Claimed'} Proxies by Country:")
            for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {country}: {count}")

            if self.verify_geo:
                fastest_country = valid_proxies[0].get('actual_country_code', valid_proxies[0]['country'])
                slowest_country = valid_proxies[-1].get('actual_country_code', valid_proxies[-1]['country'])
            else:
                fastest_country = valid_proxies[0]['country']
                slowest_country = valid_proxies[-1]['country']

            print(f"\nFastest Proxy: {valid_proxies[0]['url']} "
                  f"({fastest_country}) - {valid_proxies[0]['response_time']:.2f}s")
            if self.verify_geo and 'actual_ip' in valid_proxies[0]:
                print(f"  Exit IP: {valid_proxies[0]['actual_ip']}")

            print(f"Slowest Proxy: {valid_proxies[-1]['url']} "
                  f"({slowest_country}) - {valid_proxies[-1]['response_time']:.2f}s")

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
