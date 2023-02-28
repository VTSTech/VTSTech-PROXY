<img src="https://cdn.discordapp.com/attachments/796593977985466408/1079993165068644432/image.png">
# VTSTech-PROXY
 Python script that asynchronously checks a list of SOCKS5 proxies for anonymity and writes the results to a text file.
# Usage
<pre>
usage: VTSTech-PROXY.py [-h] [-f FILE] [-p] [-t THREADS] [-to TIMEOUT] [-c] [-u] [-v] [-s] [-4] [-4a] [-5] [-az] [-ip] [-db]

VTSTech-PROXY v0.0.4-r01

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  path to proxy list
  -p, --ping            toggle ping output
  -t THREADS, --threads THREADS
                        amount of threads to use (default: 2)
  -to TIMEOUT, --timeout TIMEOUT
                        amount of seconds before timeout (default: 8)
  -c, --code            toggle http status code output
  -u, --url             toggle test url output
  -v, --verbose         verbose, include non-200
  -s, --skip            exclude transparent proxies from output
  -4, --socks4          Use SOCKS4
  -4a, --socks4a        Use SOCKS4A
  -5, --socks5          Use SOCKS5 (default)
  -az, --azenv          Verify azenv.txt list
  -ip, --ipurl          Verify ipurl.txt list
  -db, --db             update proxy.db
</pre> 