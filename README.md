# VTSTech-PROXY
 Python script that asynchronously checks a list of SOCKS4/4A/5 proxies for anonymity and writes the results to a text file and sqlite db.
# Usage
<pre>
usage: VTSTech-PROXY.py [-h] [-f FILE] [-p] [-t THREADS] [-to TIMEOUT] [-c] [-u] [-v] [-s] [-r] [-4] [-4a] [-5] [-az] [-ip] [-st] [-xe] [-xa] [-xt]
                        [-xx] [-gen]

VTSTech-PROXY v0.0.4-r04

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  path to proxy list (default: px.txt)
  -p, --ping            toggle ping output
  -t THREADS, --threads THREADS
                        amount of threads to use (default: 2)
  -to TIMEOUT, --timeout TIMEOUT
                        amount of seconds before timeout (default: 8)
  -c, --code            toggle http status code output
  -u, --url             toggle test url output
  -v, --verbose         verbose, include non-200
  -s, --skip            exclude transparent proxies from output
  -r, --recheck         allow rechecking of known proxies
  -4, --socks4          Use SOCKS4
  -4a, --socks4a        Use SOCKS4A
  -5, --socks5          Use SOCKS5 (default)
  -az, --azenv          Verify azenv.txt list
  -ip, --ipurl          Verify ipurl.txt list
  -st, --stats          display proxy.db statistics
  -xe, --elite          export all elite.txt
  -xa, --anon           export all anon.txt
  -xt, --trans          export all trans.txt
  -xx, --all            export all px.txt
  -gen, --pxgen         generate socks4.txt and socks5.txt
</pre> 
