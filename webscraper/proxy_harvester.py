"""
Proxy Harvester - Scrapes proxy lists from various sources.

This module harvests proxies from free proxy provider websites
and extracts country-specific proxy information.
"""

import re
import time
import random
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class ProxyHarvester:
    """
    Harvests proxies from multiple sources with country filtering.
    """

    def __init__(self, countries=None, protocols=None):
        """
        Initialize the ProxyHarvester.

        Args:
            countries: List of country codes to filter (e.g., ['US', 'UK', 'CA'])
            protocols: List of protocols to filter (e.g., ['http', 'https', 'socks4', 'socks5'])
        """
        self.countries = [c.upper() for c in countries] if countries else None
        self.protocols = [p.lower() for p in protocols] if protocols else ['http', 'https']
        self.ua = UserAgent()
        self.proxies_list = []

    def _get_headers(self):
        """Generate random headers for requests."""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def _random_delay(self, min_delay=1.0, max_delay=3.0):
        """Apply random delay between requests."""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    def _harvest_free_proxy_list(self):
        """
        Harvest proxies from free-proxy-list.net
        Returns list of dict with: ip, port, country, protocol
        """
        proxies = []

        try:
            self._random_delay()
            response = requests.get(
                'https://free-proxy-list.net/',
                headers=self._get_headers(),
                timeout=15
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                table = soup.find('table', {'id': 'proxylisttable'})

                if table:
                    rows = table.find('tbody').find_all('tr')

                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 7:
                            ip = cols[0].text.strip()
                            port = cols[1].text.strip()
                            country = cols[2].text.strip()
                            https = cols[6].text.strip().lower()

                            protocol = 'https' if https == 'yes' else 'http'

                            # Filter by country if specified
                            if self.countries and country not in self.countries:
                                continue

                            # Filter by protocol
                            if protocol not in self.protocols:
                                continue

                            proxies.append({
                                'ip': ip,
                                'port': port,
                                'country': country,
                                'protocol': protocol,
                                'url': f'{protocol}://{ip}:{port}'
                            })

                    print(f"  [free-proxy-list.net] Harvested {len(proxies)} proxies")

        except Exception as e:
            print(f"  [free-proxy-list.net] Error: {e}")

        return proxies

    def _harvest_sslproxies(self):
        """
        Harvest proxies from sslproxies.org
        Returns list of dict with: ip, port, country, protocol
        """
        proxies = []

        try:
            self._random_delay()
            response = requests.get(
                'https://www.sslproxies.org/',
                headers=self._get_headers(),
                timeout=15
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                table = soup.find('table', {'id': 'proxylisttable'})

                if table:
                    rows = table.find('tbody').find_all('tr')

                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 7:
                            ip = cols[0].text.strip()
                            port = cols[1].text.strip()
                            country = cols[2].text.strip()

                            protocol = 'https'  # SSL proxies are HTTPS

                            # Filter by country if specified
                            if self.countries and country not in self.countries:
                                continue

                            # Filter by protocol
                            if protocol not in self.protocols:
                                continue

                            proxies.append({
                                'ip': ip,
                                'port': port,
                                'country': country,
                                'protocol': protocol,
                                'url': f'{protocol}://{ip}:{port}'
                            })

                    print(f"  [sslproxies.org] Harvested {len(proxies)} proxies")

        except Exception as e:
            print(f"  [sslproxies.org] Error: {e}")

        return proxies

    def _harvest_proxyscrape(self):
        """
        Harvest proxies from proxyscrape.com API
        Returns list of dict with: ip, port, country, protocol
        """
        proxies = []

        # ProxyScrape supports different protocols
        protocol_map = {
            'http': 'http',
            'https': 'http',  # HTTP proxies can often handle HTTPS
            'socks4': 'socks4',
            'socks5': 'socks5'
        }

        for protocol in self.protocols:
            if protocol not in protocol_map:
                continue

            try:
                self._random_delay()

                # ProxyScrape API endpoint
                params = {
                    'request': 'get',
                    'protocol': protocol_map[protocol],
                    'timeout': '10000',
                    'country': ','.join(self.countries) if self.countries else 'all',
                    'ssl': 'all',
                    'anonymity': 'all'
                }

                response = requests.get(
                    'https://api.proxyscrape.com/v2/',
                    params=params,
                    headers=self._get_headers(),
                    timeout=15
                )

                if response.status_code == 200:
                    lines = response.text.strip().split('\n')

                    for line in lines:
                        if ':' in line:
                            parts = line.strip().split(':')
                            if len(parts) == 2:
                                ip, port = parts

                                proxies.append({
                                    'ip': ip,
                                    'port': port,
                                    'country': 'Unknown',  # API doesn't return country in this format
                                    'protocol': protocol,
                                    'url': f'{protocol}://{ip}:{port}'
                                })

                    print(f"  [proxyscrape.com/{protocol}] Harvested {len(proxies)} proxies")

            except Exception as e:
                print(f"  [proxyscrape.com/{protocol}] Error: {e}")

        return proxies

    def _harvest_geonode(self):
        """
        Harvest proxies from geonode.com API
        Returns list of dict with: ip, port, country, protocol
        """
        proxies = []

        try:
            self._random_delay()

            # Geonode API
            params = {
                'limit': '500',
                'page': '1',
                'sort_by': 'lastChecked',
                'sort_type': 'desc'
            }

            # Add country filter if specified
            if self.countries:
                params['filterByCountry'] = ','.join(self.countries)

            # Add protocol filter
            if 'http' in self.protocols or 'https' in self.protocols:
                params['protocols'] = 'http,https'

            response = requests.get(
                'https://proxylist.geonode.com/api/proxy-list',
                params=params,
                headers=self._get_headers(),
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()

                if 'data' in data:
                    for proxy in data['data']:
                        ip = proxy.get('ip', '')
                        port = proxy.get('port', '')
                        country = proxy.get('country', 'Unknown')
                        protocols_list = proxy.get('protocols', [])

                        # Add proxy for each supported protocol
                        for proto in protocols_list:
                            proto_lower = proto.lower()
                            if proto_lower in self.protocols:
                                proxies.append({
                                    'ip': ip,
                                    'port': port,
                                    'country': country,
                                    'protocol': proto_lower,
                                    'url': f'{proto_lower}://{ip}:{port}'
                                })

                print(f"  [geonode.com] Harvested {len(proxies)} proxies")

        except Exception as e:
            print(f"  [geonode.com] Error: {e}")

        return proxies

    def harvest(self, sources=None):
        """
        Harvest proxies from all configured sources.

        Args:
            sources: List of source names to use. If None, uses all sources.
                    Available: 'free-proxy-list', 'sslproxies', 'proxyscrape', 'geonode'

        Returns:
            List of proxy dictionaries
        """
        print("=" * 70)
        print("Proxy Harvester - Collecting Proxies")
        print("=" * 70)

        if self.countries:
            print(f"Country Filter: {', '.join(self.countries)}")
        else:
            print("Country Filter: All countries")

        print(f"Protocol Filter: {', '.join(self.protocols)}")
        print("=" * 70)

        all_sources = {
            'free-proxy-list': self._harvest_free_proxy_list,
            'sslproxies': self._harvest_sslproxies,
            'proxyscrape': self._harvest_proxyscrape,
            'geonode': self._harvest_geonode
        }

        # Use specified sources or all sources
        if sources:
            sources_to_use = {k: v for k, v in all_sources.items() if k in sources}
        else:
            sources_to_use = all_sources

        print(f"\nHarvesting from {len(sources_to_use)} source(s)...\n")

        self.proxies_list = []

        for source_name, harvest_func in sources_to_use.items():
            print(f"Harvesting from {source_name}...")
            try:
                proxies = harvest_func()
                self.proxies_list.extend(proxies)
            except Exception as e:
                print(f"  Error harvesting from {source_name}: {e}")

        # Remove duplicates based on URL
        unique_proxies = {}
        for proxy in self.proxies_list:
            unique_proxies[proxy['url']] = proxy

        self.proxies_list = list(unique_proxies.values())

        print("\n" + "=" * 70)
        print(f"Total Unique Proxies Harvested: {len(self.proxies_list)}")
        print("=" * 70)

        # Print summary by country
        if self.proxies_list:
            country_counts = {}
            for proxy in self.proxies_list:
                country = proxy.get('country', 'Unknown')
                country_counts[country] = country_counts.get(country, 0) + 1

            print("\nProxies by Country:")
            for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {country}: {count}")

        return self.proxies_list

    def save_to_file(self, filename='proxies.txt', format='url'):
        """
        Save harvested proxies to a file.

        Args:
            filename: Output filename
            format: Output format - 'url' (protocol://ip:port) or 'simple' (ip:port)
        """
        if not self.proxies_list:
            print("No proxies to save. Run harvest() first.")
            return

        with open(filename, 'w') as f:
            for proxy in self.proxies_list:
                if format == 'url':
                    f.write(f"{proxy['url']}\n")
                elif format == 'simple':
                    f.write(f"{proxy['ip']}:{proxy['port']}\n")

        print(f"\nSaved {len(self.proxies_list)} proxies to {filename}")

    def get_proxy_list(self, format='url'):
        """
        Get list of proxies in specified format.

        Args:
            format: 'url' (protocol://ip:port), 'simple' (ip:port), or 'dict' (full dict)

        Returns:
            List of proxies in specified format
        """
        if format == 'url':
            return [p['url'] for p in self.proxies_list]
        elif format == 'simple':
            return [f"{p['ip']}:{p['port']}" for p in self.proxies_list]
        else:  # dict
            return self.proxies_list
