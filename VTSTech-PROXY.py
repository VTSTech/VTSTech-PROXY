# Program: VTSTech-PROXY.py
# Description: Python script that asynchronously checks a list of SOCKS5 proxies for anonymity and writes the results to a text file.
# Author: Written by Veritas//VTSTech (veritas@vts-tech.org)
# GitHub: https://github.com/Veritas83
# Homepage: www.VTS-Tech.org
# Dependencies: aiohttp
# pip install aiohttp tqdm
# OpenAI's ChatCPT wrote r00, I modified it from there to be r01.
import aiohttp
import asyncio
import signal
import sys
import random
import time
import argparse
from tqdm import tqdm
build = "VTSTech-PROXY v0.0.2-r05"
sys.tracebacklimit = 0
def handle_interrupt(signal, frame):
    print("\nStopping current proxy check...")
    sys.exit(0)
signal.signal(signal.SIGINT, handle_interrupt)
parser = argparse.ArgumentParser(description=build)
parser.add_argument("proxies_file", help="path to proxies file")
parser.add_argument("-p", "--ping", action="store_true", help="toggle ping output")
parser.add_argument("-t", "--threads", type=int, default=2, help="amount of threads to use (default: 2)")
parser.add_argument("-c", "--code", action="store_true", help="toggle http status code output")
parser.add_argument("-u", "--url", action="store_true", help="toggle test url output")
parser.add_argument("-4", "--socks4", action="store_true", help="Use SOCKS4")
parser.add_argument("-5", "--socks5", action="store_true", help="Use SOCKS5 (default)")
args = parser.parse_args()
proxies_file = args.proxies_file
with open(proxies_file) as f:
    proxies = [line.strip() for line in f.readlines()]
with open("azenv.txt") as f:
    test_urls = [line.strip() for line in f.readlines()]
print(f"VTSTech-PROXY {build} https://www.VTS-Tech.org/\nStarting proxy check for {len(proxies)} proxies...\n")
with open("prox.txt", "w") as outfile:
    outfile.write(f"VTSTech-PROXY {build} https://www.VTS-Tech.org/\nStarting proxy check for {len(proxies)} proxies...\n")
    async def check_proxy(session, proxy, pbar, semaphore):
        #time.sleep(0.1)
        proxy_host, proxy_port = proxy.split(":")
        proxy_port = int(proxy_port)
        socks_uri = "socks5://"
        if args.socks4:
        	socks_uri = "socks4://"
        test_url = random.choice(test_urls)
        try:
            async with semaphore:
	            async with session.get(test_url, proxy=f'{socks_uri}{proxy_host}:{proxy_port}', timeout=8) as response:
	                if response.status < 503:
	                    is_error = False
	                    is_timeout = False
	                    if proxy_host in await response.text():
	                        is_proxy_ip_present = True
	                        output = f"{proxy_host}:{proxy_port}"
	                    else:
	                        is_proxy_ip_present = False
	                        output = f"{proxy_host}:{proxy_port} ANON: NO."
	                else:
	                    is_error = False
	                    is_timeout = False                    
	                    output = f"{proxy_host}:{proxy_port} {response.status} {test_url}."
	                    is_proxy_ip_present = False
        except asyncio.TimeoutError as e:
            is_timeout = True
            is_error = False
            is_proxy_ip_present = False
            output = f"TIMEOUT {proxy_host}:{proxy_port}"
            pbar.update(1)
        except Exception as e:
            is_error = True
            is_proxy_ip_present = False
            is_timeout = False
            output = f"ERROR {proxy_host}:{proxy_port}"
            pbar.update(1)
        if args.code:
            try:
                    output += f" CODE: {response.status}"
            except:
                pass
        if args.url:
            try:
                    output += f" URL: {test_url}"
            except:
                pass
        if args.ping:
            try:
                start_time = time.monotonic()
                async with session.get(test_url, proxy=f'{socks_uri}{proxy_host}:{proxy_port}', timeout=8) as response:
                    latency = time.monotonic() - start_time
                    output += f" PING: {round(latency * 1000, 2)}ms"
            except:
                pass   
        pbar.update(1)
        return is_proxy_ip_present, is_error, is_timeout, output

    async def main():
	    if args.threads:
	    	try:
	    		threads = args.threads
	    	except:
	    		pass
	    semaphore = asyncio.Semaphore(value=threads)
	    async with semaphore:
		    async with aiohttp.ClientSession() as session:
		        tasks = []
		        total_proxies = len(proxies)
		        with tqdm(total=total_proxies) as pbar:
		            for proxy in proxies:
		                task = asyncio.create_task(check_proxy(session, proxy, pbar, semaphore))
		                tasks.append(task)
		            results = await asyncio.gather(*tasks)
		            for is_proxy_ip_present, is_error, is_timeout, output in results:
		                if is_proxy_ip_present:
		                    print(output)
		                    outfile.write(output + "\n")
		                if not is_timeout and not is_error and not is_proxy_ip_present:
		                    print(output)
		                    outfile.write(output + "\n")
    asyncio.run(main())            
