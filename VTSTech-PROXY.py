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
import requests
import sqlite3
import pxgen
import subprocess
import platform

build = "VTSTech-PROXY v0.0.4-r06"
system = platform.system()
#print(system)
def get_ping_latency(proxy_host):
    try:
        if system == "Windows":
	        result = subprocess.run(['ping.exe', '-n', '1', '-l', '1', f"{proxy_host}"], capture_output=True, text=True, timeout=5)
	        if "Reply from" in result.stdout:
	            latency = float(result.stdout.split("time=")[1].split("ms")[0])
	            return round(latency, 2)
        else:
	        result = subprocess.run(['ping', '-c', '1', '-W', '1', f"{proxy_host}"], capture_output=True, text=True, timeout=5)
	        if "1 received" in result.stdout:
	            latency = float(result.stdout.split("time=")[1].split(" ms")[0])
	            return round(latency, 2)
    except Exception:
        pass
    return None

def handle_interrupt(signal, frame):
    print("\nStopping current proxy check...")
    sys.exit(0)
sys.tracebacklimit = 0
signal.signal(signal.SIGINT, handle_interrupt)
parser = argparse.ArgumentParser(description=build)
parser.add_argument("-f", "--file", default="px.txt", help="path to proxy list (default: px.txt)")
parser.add_argument("-p", "--ping", action="store_true", help="toggle ping output")
parser.add_argument("-t", "--threads", type=int, default=2, help="amount of threads to use (default: 2)")
parser.add_argument("-to", "--timeout", type=int, default=8, help="amount of seconds before timeout (default: 8)")
parser.add_argument("-c", "--code", action="store_true", help="toggle http status code output")
parser.add_argument("-u", "--url", action="store_true", help="toggle test url output")
parser.add_argument("-v", "--verbose", action="store_true", help="verbose, include non-200")
parser.add_argument("-s", "--skip", action="store_true", help="exclude transparent proxies from output")
parser.add_argument("-r", "--recheck", action="store_true", help="allow rechecking of known proxies")
parser.add_argument("-4", "--socks4", action="store_true", help="Use SOCKS4")
parser.add_argument("-4a", "--socks4a", action="store_true", help="Use SOCKS4A")
parser.add_argument("-5", "--socks5", action="store_true", help="Use SOCKS5 (default)")
parser.add_argument("-az", "--azenv", action="store_true", help="Verify azenv.txt list")
parser.add_argument("-ip", "--ipurl", action="store_true", help="Verify ipurl.txt list")
parser.add_argument("-db", "--db", action="store_true", help="update proxy.db with results of previous scan")
parser.add_argument("-dp", "--dupes", action="store_true", help="remove duplicates from proxy.db based on IP alone")
parser.add_argument("-st", "--stats", action="store_true", help="display proxy.db statistics")
parser.add_argument("-xe", "--elite", action="store_true", help="export all elite.txt")
parser.add_argument("-xa", "--anon", action="store_true", help="export all anon.txt")
parser.add_argument("-xt", "--trans", action="store_true", help="export all trans.txt")
parser.add_argument("-xx", "--all", action="store_true", help="export all px.txt")
parser.add_argument("-gen", "--pxgen", action="store_true", help="generate socks4.txt and socks5.txt")
args = parser.parse_args()
proxies_file = args.file
if args.socks4 or args.socks4a:
    dbname="socks4.db"
else:
    dbname="proxy.db"
def updatedb():
    # Open a connection to the SQLite database
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    print(f"Updating {dbname} ...\n")
    # Create the table to hold the data
    c.execute('CREATE TABLE IF NOT EXISTS proxies (ip_port TEXT PRIMARY KEY, anonymity TEXT, level TEXT, url TEXT, ping REAL, last_tested DATE)')

    # Open the text file and read in the lines
    with open('prox.txt', 'r') as f:
        lines = f.readlines()[2:]

    # Remove new line characters and split lines into columns
    for line in lines:
        line = line.strip()
        columns = line.split(' ')
        ip_port = columns[0]
        anonymity = columns[4]
        level = columns[3]
        url = ''
        ping = ''
        for i in range(5, len(columns)):
            if columns[i].startswith('URL:'):
                url = columns[i+1]
            elif columns[i].startswith('PING:'):
                ping = columns[i+1][:-2]
        
        # Check if the proxy already exists in the database
        result = c.execute('SELECT * FROM proxies WHERE ip_port = ?', (ip_port,)).fetchone()
        if result:
            # Update the values
            c.execute('UPDATE proxies SET anonymity = ?, level = ?, url = ?, ping = ?, last_tested = date() WHERE ip_port = ?', (anonymity, level, url, ping, ip_port))
        else:
            # Insert a new row
            c.execute('INSERT INTO proxies VALUES (?, ?, ?, ?, ?, date())', (ip_port, anonymity, level, url, ping))

    # Commit the changes to the database and close the connection
    conn.commit()
    conn.close()
def get_prox():
    output_file_path = "socks5.txt"
    pxgen.download_and_merge_text_files(pxgen.socks5, output_file_path)
    print("socks5.txt written!")
    pxgen.remove_duplicate_lines("./socks5.txt")
    print("duplicates removed!")

    output_file_path = "socks4.txt"
    pxgen.download_and_merge_text_files(pxgen.socks4, output_file_path)
    print("socks4.txt written!")
    pxgen.remove_duplicate_lines("./socks4.txt")
    print("duplicates removed!")
with open("ipurl.txt") as f:
    ip_urls = [line.strip() for line in f.readlines()]    
def get_public_ip():
    response = requests.get(random.choice(ip_urls)).text
    return response
def export_elite_proxies():
    with sqlite3.connect(dbname) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM proxies WHERE level='1'")
        results = c.fetchall()
        with open('elite.txt', 'w') as f:
            for row in results:
                f.write(row[0] + '\n')
        print(f'Successfully exported {len(results)} Elite proxies to elite.txt')
def export_anon_proxies():
    with sqlite3.connect(dbname) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM proxies WHERE level='2'")
        results = c.fetchall()
        with open('anon.txt', 'w') as f:
            for row in results:
                f.write(row[0] + '\n')
        print(f'Successfully exported {len(results)} Anonymous proxies to anon.txt')    
def export_trans_proxies():
    with sqlite3.connect(dbname) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM proxies WHERE level='3'")
        results = c.fetchall()
        with open('trans.txt', 'w') as f:
            for row in results:
                f.write(row[0] + '\n')
        print(f'Successfully exported {len(results)} Transparent proxies to trans.txt')
def export_all_proxies():
    with sqlite3.connect(dbname) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM proxies")
        results = c.fetchall()
        with open('px.txt', 'w') as f:
            for row in results:
                f.write(row[0] + '\n')
        print(f'Successfully exported {len(results)} proxies to px.txt')         
def dbstats():
    conn = sqlite3.connect(dbname)
    print(f"Accessing {dbname} ...\n")
    c = conn.cursor()
    total_proxies = c.execute('SELECT COUNT(*) FROM proxies').fetchone()[0]
    total_elite = c.execute('SELECT COUNT(*) FROM proxies WHERE level = 1').fetchone()[0]
    total_anon = c.execute('SELECT COUNT(*) FROM proxies WHERE level = 2').fetchone()[0]
    total_transparent = c.execute('SELECT COUNT(*) FROM proxies WHERE level = 3').fetchone()[0]
    conn.close()
    print(f"Total Proxies: {total_proxies}")
    print(f"Total Elite: {total_elite}")
    print(f"Total Anonymous: {total_anon}")
    print(f"Total Transparent: {total_transparent}")
def remove_duplicates_by_ip():
    # Open a connection to the SQLite database
    conn = sqlite3.connect(dbname)
    print(f"Accessing {dbname} ...\n")
    c = conn.cursor()

    # Remove duplicates based on IP address
    ips = set()
    duplicates = []
    for row in c.execute('SELECT rowid, ip_port FROM proxies'):
        ip = row[1].split(':')[0]
        if ip in ips:
            duplicates.append(row[0])
        else:
            ips.add(ip)

    for rowid in duplicates:
        c.execute('DELETE FROM proxies WHERE rowid = ?', (rowid,))
        print(f"deleting {rowid}")

    # Commit the changes to the database and close the connection
    conn.commit()
    conn.close()
with open(proxies_file) as f:
    proxies = [line.strip() for line in f.readlines()]
with open("azenv.txt") as f:
    test_urls = [line.strip() for line in f.readlines()]
def verify_azenv():
    wan_ip=get_public_ip()
    verified_urls=""
    for x in test_urls:
        try:
            r = requests.get(x, timeout=args.timeout)
            if r.status_code==200 and wan_ip in r.text:
                verified_urls+=f"{x}\n"            
        except:
            print(f"ERROR: {r.status_code} {x} ")
    print("\nazenv.txt verification complete!\n")    
    return verified_urls
def verify_ipurl():
    wan_ip=get_public_ip()
    verified_ipurls=""
    for x in ip_urls:
        try:
            r = requests.get(x, timeout=args.timeout)
            if r.status_code==200 and wan_ip in r.text:
                verified_ipurls+=f"{x}\n"            
        except:
            print(f"ERROR: {x}")
    print("\nipurl.txt verification complete!\n")    
    return verified_ipurls    
print(f"{build} VTS-Tech.org github.com/Veritas83\n")
if args.azenv:
    print("Verifying azenv.txt ...\n")
    print(verify_azenv())
    quit()
if args.ipurl:
    print("Verifying ipurl.txt ...\n")
    print(verify_ipurl())
    quit()
if args.db:
    updatedb()
    quit()
if args.elite:
    export_elite_proxies()
    quit()    
if args.anon:
    export_anon_proxies()
    quit()    
if args.trans:
    export_trans_proxies()
    quit()    
if args.all:
    export_all_proxies()
    quit()
if args.stats:
    dbstats()
    quit()
if args.pxgen:
    get_prox()
    quit()    
if args.dupes:
    remove_duplicates_by_ip()
    quit() 
with open("prox.txt", "w") as outfile:
    wan_ip=get_public_ip()
    outfile.write(f"{build} VTS-Tech.org github.com/Veritas83\nStarting proxy check for {len(proxies)} proxies...\n")
    print(f"Starting proxy check for {len(proxies)} proxies...\n")
    # Open a connection to the SQLite database
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    print(f"Accessing {dbname} ...\n")
    async def check_proxy(session, proxy, semaphore):
        #time.sleep(0.1)
        proxy_host, proxy_port = proxy.split(":")
        proxy_port = int(proxy_port)
        socks_uri = "socks5://"
        output=str(0)
        if args.socks4:
        	socks_uri = "socks4://"
        elif args.socks4a:
        	socks_uri = "socks4a://"
        test_url = random.choice(test_urls)
        # Check if the proxy already exists in the database
        result = c.execute('SELECT * FROM proxies WHERE ip_port = ?', (proxy,)).fetchone()
        if result and not args.recheck:
            print(f"{proxy} already exists in the database!")
        else:
            try:
                async with semaphore:
	                async with session.get(test_url, proxy=f'{socks_uri}{proxy_host}:{proxy_port}', timeout=args.timeout) as response:
	                    is_error = False
	                    is_timeout = False
	                    is_proxy_ip_present = False
	                    output=str(0)
	                    if response.status < 503:
	                        if proxy_host in await response.text():
	                            is_proxy_ip_present = True
	                            if ("HTTP_X_FORWARDED_FOR" and wan_ip) in await response.text() and not args.skip:
	                                output = f"{proxy_host}:{proxy_port} ANON LV: 3 (transparent)"
	                            elif ("HTTP_X_FORWARDED_FOR") in await response.text():
	                                if wan_ip not in await response.text():
	                                    output = f"{proxy_host}:{proxy_port} ANON LV: 2 (anonymous)"
	                            elif ("HTTP_X_FORWARDED_FOR" and wan_ip) not in await response.text():
	                                if f"REMOTE_ADDR = {proxy_host}"in await response.text():
	                                    output = f"{proxy_host}:{proxy_port} ANON LV: 1 (elite)"
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
	                                latency = get_ping_latency(proxy_host)
	                                if latency:
	                                    output += f" PING: {latency}ms"
	                            if is_proxy_ip_present == True and len(output)>9 and output[0] != "0":
	                                print(output)
	                        else:
	                            is_proxy_ip_present = False
	                            if args.verbose:	                        
	                                output = f"{proxy_host}:{proxy_port} {response.status} {test_url}."
	                                print(output)	                            
	                    else:
	                        is_error = False
	                        is_timeout = False  
	                        if args.verbose:
	                            output = f"{proxy_host}:{proxy_port} {response.status} {test_url}."
	                            print(output)
	                        is_proxy_ip_present = False
	                        output = f"{proxy_host}:{proxy_port} {response.status} {test_url}."
            except asyncio.TimeoutError as e:
                is_timeout = True
                is_error = False
                is_proxy_ip_present = False
                if args.verbose:
                	output = f"TIMEOUT {proxy_host}:{proxy_port}"
            except Exception as e:
                is_error = True
                is_proxy_ip_present = False
                is_timeout = False
                if args.verbose:
                	output = f"ERROR {proxy_host}:{proxy_port}"   
            if len(output)>9 and output[0] != "0" and is_error==False and is_timeout==False and is_proxy_ip_present==True:
                outfile.write(output + "\n")
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
                is_error = False
                is_timeout = False
                is_proxy_ip_present = False
                output=""
                tasks = []
                if proxies is not None:
                    total_proxies = len(proxies)
                    for proxy in proxies:
                        task = asyncio.create_task(check_proxy(session, proxy, semaphore))
                        if task is not None:
                            tasks.append(task)
                    results = await asyncio.gather(*tasks)
    asyncio.run(main())
