<img src="https://imgur.com/dCwo7KJ.png">
# VTSTech-PROXY
 Python script that asynchronously checks a list of SOCKS5 proxies for anonymity and writes the results to a text file.
# Usage
<pre>
usage: VTSTech-PROXY.py [-h] [-p] [-c] [-u] [-4] [-5] proxies_file

VTSTech-PROXY v0.0.2-r03

positional arguments:
  proxies_file  path to proxies file

options:
  -h, --help    show this help message and exit
  -p, --ping    toggle ping output
  -c, --code    toggle http status code output
  -u, --url     toggle test url output
  -4, --socks4  Use SOCKS4
  -5, --socks5  Use SOCKS5 (default)
</pre> 