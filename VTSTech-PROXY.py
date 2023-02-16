# Program: VTSTech-PROXY.py
# Description: Python script that asynchronously checks a list of SOCKS5 proxies for anonymity and writes the results to a text file.
# Author: Written by Veritas//VTSTech (veritas@vts-tech.org)
# GitHub: https://github.com/Veritas83
# Homepage: www.VTS-Tech.org
# Dependencies: aiohttp async-timeout
# pip install aiohttp async-timeout
# OpenAI's ChatCPT wrote r00, I modified it from there to be r01.

import aiohttp
import asyncio
import signal
import sys
import random
import time
import argparse

build = "v0.0.1-r05"

# Handle the KeyboardInterrupt signal by stopping the current proxy check
def handle_interrupt(signal, frame):
    print("\nStopping current proxy check...")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_interrupt)

# Read proxies from text file
parser = argparse.ArgumentParser(description="VTSTech-PROXY proxy checker")
parser.add_argument("proxies_file", help="path to proxies file")
parser.add_argument("-p", "--ping", action="store_true", help="toggle ping output")
args = parser.parse_args()

proxies_file = args.proxies_file

with open(proxies_file) as f:
    proxies = [line.strip() for line in f.readlines()]

with open("azenv.txt") as f:
    test_urls = [line.strip() for line in f.readlines()]

print(f"VTSTech-PROXY {build} https://www.VTS-Tech.org/\n")
print(f"Starting proxy check for {len(proxies)} proxies...\n")

# Open a file handle to write the results to a text file
with open("prox.txt", "w") as outfile:
    # Call the proxy script for each proxy
    outfile.write(f"VTSTech-PROXY {build} https://www.VTS-Tech.org/\nStarting proxy check for {len(proxies)} proxies...\n")
    async def check_proxy(session, proxy):
        time.sleep(0.1)
        # Extract proxy host and port from string
        proxy_host, proxy_port = proxy.split(":")
        proxy_port = int(proxy_port)
        # Choose a random URL from the list to test the proxy with
        test_url = random.choice(test_urls)
        try:
            # Test the proxy by making a request
            async with session.get(test_url, proxy=f'socks5://{proxy_host}:{proxy_port}', timeout=8) as response:
                if response.status == 200:
                    # Check if the proxy IP is present in the response HTML
                    if proxy_host in await response.text():
                        is_proxy_ip_present = True
                        output = f"{proxy_host}:{proxy_port}"
                    else:
                        is_proxy_ip_present = False
                        output = f"SOCKS5 {proxy_host}:{proxy_port} {response.status} {test_url} ANON: NO."
                else:
                    output = f"SOCKS5 {proxy_host}:{proxy_port} {response.status} {test_url}."
                    is_proxy_ip_present = False
        except asyncio.TimeoutError as e:
            is_proxy_ip_present = False
            output = f"SOCKS5 {proxy_host}:{proxy_port} TIMEOUT: {e}."
        except Exception as e:
            is_proxy_ip_present = False
            output = f"SOCKS5 {proxy_host}:{proxy_port} ERROR: {e}."
        if args.ping:
            try:
                # Ping the proxy to check its latency
                start_time = time.monotonic()
                async with session.get(test_url, proxy=f'socks5://{proxy_host}:{proxy_port}', timeout=8) as response:
                    latency = time.monotonic() - start_time
                    output += f" PING: {round(latency * 1000, 2)}ms"
            except:
                pass
        return is_proxy_ip_present, output

    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = []
            for proxy in proxies:
                tasks.append(check_proxy(session, proxy))
            results = await asyncio.gather(*tasks)
            for is_proxy_ip_present, output in results:
                if is_proxy_ip_present:
                    print(output)
                    # Write the output to the text file
                    outfile.write(output + "\n")
    asyncio.run(main())            
