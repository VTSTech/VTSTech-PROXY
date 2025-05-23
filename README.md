# VTSTech-PROXY
 Python script that asynchronously checks a list of SOCKS4/4A/5 proxies for anonymity and writes the results to a text file and sqlite db.
# Usage
<pre>
$ python VTSTech-PROXY.py -h                               

██╗   ██╗████████╗███████╗████████╗███████╗ ██████╗██╗  ██╗
╚██╗ ██╔╝╚══██╔══╝██╔════╝╚══██╔══╝██╔════╝██╔════╝██║  ██║
 ╚████╔╝    ██║   ███████╗   ██║   █████╗  ██║     ███████║
  ╚██╔╝     ██║   ╚════██║   ██║   ██╔══╝  ██║     ██╔══██║
   ██║      ██║   ███████║   ██║   ███████╗╚██████╗██║  ██║
   ╚═╝      ╚═╝   ╚══════╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝

VTSTech-PROXY v0.0.5-r09 www.vts-tech.org github.com/VTSTech
usage: VTSTech-PROXY.py [-h] [-f FILE] [-ua UA] [-g] [-st] [-t THREADS] [-to TIMEOUT] [-r] [-c] [-4] [-4a] [-xx] [-xe] [-xa] [-v]

VTSTech-PROXY v0.0.5-r09 www.vts-tech.org github.com/VTSTech

options:
  -h, --help            show this help message and exit
  -f, --file FILE       Proxy list file
  -ua, --ua UA          Set custom User-Agent string
  -g, --gen             Generate fresh proxy list from online sources
  -st, --stats          Show minimal database statistics
  -t, --threads THREADS
                        Concurrency level
  -to, --timeout TIMEOUT
                        Timeout seconds
  -r, --recheck         Recheck known proxies
  -c, --clean           Recheck all DB proxies and remove offline ones
  -4, --socks4          Use SOCKS4
  -4a, --socks4a        Use SOCKS4A
  -xx, --export-all     Export all proxies to file
  -xe, --export-elite   Export elite proxies to file
  -xa, --export-anonymous
                        Export anonymous proxies to file
  -v, --verbose         Show errors
</pre> 
