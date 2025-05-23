# Program: VTSTech-PROXY.py
# Description: Python script that asynchronously checks a list of SOCKS5 proxies for anonymity and writes the results to a text file.
# Author: Written by Veritas//VTSTech (veritas@vts-tech.org)
# GitHub: https://github.com/VTSTech
# Homepage: www.VTS-Tech.org
# Dependencies: aiohttp
# pip install aiohttp aiohttp_socks tqdm

import aiohttp
import asyncio
import argparse
import sqlite3
import platform
import subprocess
from tqdm import tqdm
from datetime import datetime
import random
from aiohttp_socks import ProxyConnector, ProxyType
from pxgen import download_and_merge_text_files, socks4, socks5

BANNER = r"""
██╗   ██╗████████╗███████╗████████╗███████╗ ██████╗██╗  ██╗
╚██╗ ██╔╝╚══██╔══╝██╔════╝╚══██╔══╝██╔════╝██╔════╝██║  ██║
 ╚████╔╝    ██║   ███████╗   ██║   █████╗  ██║     ███████║
  ╚██╔╝     ██║   ╚════██║   ██║   ██╔══╝  ██║     ██╔══██║
   ██║      ██║   ███████║   ██║   ███████╗╚██████╗██║  ██║
   ╚═╝      ╚═╝   ╚══════╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝
"""

system = platform.system()
build = "VTSTech-PROXY v0.0.6-r09 www.vts-tech.org github.com/VTSTech"
DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def print_banner():
    print(BANNER)
    print(build)
    
class ProxyChecker:
    def __init__(self, args):
        self.args = args
        self.user_agent = args.ua if args.ua else DEFAULT_UA
        self.headers = {'User-Agent': self.user_agent}        
        self.db_name = "socks4.db" if (args.socks4 or args.socks4a) else "proxy.db"
        self.proxies = []
        self.results = []
        self.ip_urls = self.load_file("ipurl.txt")
        self.valid_counter = 0
        self.test_urls = [
            "http://httpbin.org/ip",
            "http://api.ipify.org?format=json",
            "https://jsonip.com/",
            "https://l2.io/ip.json",
            "https://api.ip.sb/ip",
            "http://ipinfo.io/json"
        ]
        self.wan_ip = None
        self.init_database()
        self.load_proxies()

    def load_file(self, filename):
        with open(filename) as f:
            return [line.strip() for line in f if line.strip()]

    def init_database(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS proxies (
                         ip_port TEXT PRIMARY KEY, 
                         anonymity TEXT, 
                         level INTEGER, 
                         url TEXT, 
                         ping REAL, 
                         last_tested DATE)''')

    def load_proxies(self):
        with open(self.args.file) as f:
            self.proxies = [line.strip() for line in f if ':' in line.strip()]
        
        if not self.args.recheck:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.execute("SELECT ip_port FROM proxies")
                existing = {row[0] for row in cursor.fetchall()}
            self.proxies = [p for p in self.proxies if p not in existing]

    async def get_public_ip(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(random.choice(self.ip_urls), timeout=5) as response:
                    return await response.text()
        except:
            return "Unknown"

    def get_ping_latency(self, host):
        param = ['-n', '1', '-l', '1'] if system == "Windows" else ['-c', '1', '-W', '1']
        try:
            result = subprocess.run(['ping'] + param + [host], 
                                  capture_output=True, text=True, timeout=2)
            if "time=" in result.stdout:
                return round(float(result.stdout.split("time=")[1].split(" ms")[0]), 2)
        except:
            return None

    async def check_proxy(self, proxy, semaphore, pbar):
        async with semaphore:
            try:
                host, port = proxy.split(":", 1)
                proxy_type = ProxyType.SOCKS4 if self.args.socks4 else ProxyType.SOCKS5
                connector = ProxyConnector(
                    proxy_type=proxy_type,
                    host=host,
                    port=int(port),
                    rdns=True
                )
                
                async with aiohttp.ClientSession(connector=connector, headers=self.headers) as session:
                    for test_url in random.sample(self.test_urls, 2):
                        try:
                            async with session.get(test_url, timeout=self.args.timeout,headers=self.headers) as response:
                                if response.status == 200:
                                    headers = response.headers
                                    content = await response.text()
                                    if self.wan_ip in content:
                                        anonymity = 'Transparent'
                                        level = 3                                   
                                    elif any(h in headers for h in ['X-Forwarded-For', 'Via', 'Forwarded']):
                                        anonymity = 'Anonymous'
                                        level = 2
                                    else:
                                        anonymity = 'Elite'
                                        level = 1

                                    latency = self.get_ping_latency(host)
                                    result = {
                                        'ip_port': proxy,
                                        'anonymity': anonymity,
                                        'level': level,
                                        'url': test_url,
                                        'ping': latency,
                                        'last_tested': datetime.now().strftime('%Y-%m-%d')
                                    }
                                    self.results.append(result)
                                    self.valid_counter += 1
                                    if self.valid_counter % 3 == 0:
                                        await self.update_database()
                                        self.results = []  # Clear the in-memory results that were just written                                    
                                    ping_display = f" | Ping: {latency}ms" if latency is not None else ""
                                    pbar.write(f"VALID {proxy} | Level {level} ({anonymity}){ping_display}")
                                    return
                        except Exception as e:
                            if self.args.verbose:
                                pbar.write(f"ERROR {proxy} - {str(e)}")
            except Exception as e:
                if self.args.verbose:
                    pbar.write(f"CONNECTION FAILED {proxy} - {str(e)}")
            finally:
                pbar.update(1)

    async def update_database(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.executemany('''INSERT OR REPLACE INTO proxies 
                              VALUES (?,?,?,?,?,?)''', 
                              [(r['ip_port'], r['anonymity'], r['level'], 
                               r['url'], r['ping'], r['last_tested']) for r in self.results])
            conn.commit()

    async def clean_offline_proxies(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ip_port FROM proxies")
            db_proxies = [row[0] for row in cursor.fetchall()]

        self.results = []  # Reset previous results
        self.proxies = db_proxies  # Use proxies from the DB

        print(f"\nRechecking {len(self.proxies)} proxies from the database...")

        self.wan_ip = await self.get_public_ip()
        semaphore = asyncio.Semaphore(self.args.threads)

        with tqdm(total=len(self.proxies), desc="Rechecking proxies") as pbar:
            tasks = [self.check_proxy(p, semaphore, pbar) for p in self.proxies]
            await asyncio.gather(*tasks)

        valid_set = {r['ip_port'] for r in self.results}
        to_delete = list(set(self.proxies) - valid_set)

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.executemany("DELETE FROM proxies WHERE ip_port = ?", [(p,) for p in to_delete])
            conn.commit()

        print(f"\nRemoved {len(to_delete)} offline proxies from {self.db_name}")
        
    async def run(self):
        self.wan_ip = await self.get_public_ip()
        semaphore = asyncio.Semaphore(self.args.threads)
        with tqdm(total=len(self.proxies), desc="Checking proxies") as pbar:
            tasks = [self.check_proxy(p, semaphore, pbar) for p in self.proxies]
            await asyncio.gather(*tasks)
        if self.results:
            await self.update_database()

def show_minimal_stats(db_name):
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM proxies")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT level, COUNT(*) FROM proxies GROUP BY level")
            rows = cursor.fetchall()
            levels = {1: 0, 2: 0, 3: 0}
            for level, count in rows:
                levels[int(level)] = count  # Convert string to int
                
            print(f"\nDatabase: {db_name}")
            print(f"Total: {total}")
            print(f"Elite: {levels[1]} | Anonymous: {levels[2]} | Transparent: {levels[3]}")
           #print("Raw level counts:", rows)

    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")

def export_proxies(db_name, level=None, filename=None):
    """
    Export proxies from DB to a file.
    If level is None, export all.
    level = 1 (Elite), 2 (Anonymous)
    """
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            if level is None:
                cursor.execute("SELECT ip_port FROM proxies")
                desc = "all"
            else:
                cursor.execute("SELECT ip_port FROM proxies WHERE level = ?", (level,))
                desc = {1: "elite", 2: "anonymous"}.get(level, "filtered")

            rows = cursor.fetchall()
            proxies = [row[0] for row in rows]

        if not filename:
            filename = f"export_{desc}_proxies.txt"

        with open(filename, "w") as f:
            f.write("\n".join(proxies))

        print(f"Exported {len(proxies)} {desc} proxies to {filename}")

    except sqlite3.Error as e:
        print(f"Error exporting proxies: {e}")

def main():
    print_banner()
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default="socks5.txt", help="Proxy list file")
    parser.add_argument("-ua", "--ua", help="Set custom User-Agent string")
    parser.add_argument("-g", "--gen", action="store_true", help="Generate fresh proxy list from online sources")
    parser.add_argument("-st", "--stats", action="store_true", help="Show minimal database statistics")    
    parser.add_argument("-t", "--threads", type=int, default=8, help="Concurrency level")
    parser.add_argument("-to", "--timeout", type=int, default=8, help="Timeout seconds")
    parser.add_argument("-r", "--recheck", action="store_true", help="Recheck known proxies")
    parser.add_argument("-c", "--clean", action="store_true", help="Recheck all DB proxies and remove offline ones")
    parser.add_argument("-4", "--socks4", action="store_true", help="Use SOCKS4")
    parser.add_argument("-4a", "--socks4a", action="store_true", help="Use SOCKS4A")
    parser.add_argument("-xx", "--export-all", action="store_true", help="Export all proxies to file")
    parser.add_argument("-xe", "--export-elite", action="store_true", help="Export elite proxies to file")
    parser.add_argument("-xa", "--export-anonymous", action="store_true", help="Export anonymous proxies to file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show errors")
    args = parser.parse_args()

    if args.stats:
        db_name = "socks4.db" if (args.socks4 or args.socks4a) else "proxy.db"
        show_minimal_stats(db_name)
        return
    if args.clean:
        checker = ProxyChecker(args)
        asyncio.run(checker.clean_offline_proxies())
        return            
    if args.export_all or args.export_elite or args.export_anonymous:
        db_name = "socks4.db" if (args.socks4 or args.socks4a) else "proxy.db"
        if args.export_all:
            export_proxies(db_name)
        if args.export_elite:
            export_proxies(db_name, level=1)
        if args.export_anonymous:
            export_proxies(db_name, level=2)
        return        
    if args.gen:
        print("\nGenerating proxy list from online sources...")
        urls = socks4 if (args.socks4 or args.socks4a) else socks5
        download_and_merge_text_files(urls, args.file)
        print(f"Proxy list saved to {args.file}")
        return
    checker = ProxyChecker(args)
    asyncio.run(checker.run())
    #print(f"\nFound {len(checker.results)} valid proxies out of {len(checker.proxies)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
