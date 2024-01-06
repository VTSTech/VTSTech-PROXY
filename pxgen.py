# Program: pxgen.py
# Description: Python module creates a list of SOCKS4/5 proxies from various sources
# Author: Written by Veritas//VTSTech (veritas@vts-tech.org)
# GitHub: https://github.com/VTSTech
# Homepage: www.VTS-Tech.org

import requests

socks5 = [
    "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt",
    "https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/socks5.txt"
]
socks4 = [
    "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt",
    "https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/socks4.txt"
]

def remove_duplicate_lines(file_path):
    with open(file_path, "r") as input_file:
        # Read in all the lines from the input file
        lines = input_file.readlines()

    # Convert the list of lines to a set to remove duplicates
    unique_lines = set(lines)

    with open(file_path, "w") as output_file:
        # Write the unique lines back to the input file
        output_file.writelines(unique_lines)
        
def download_and_merge_text_files(urls, output_file_path):
    # Create an empty set to store the unique lines
    unique_lines = set()

    # Loop through each URL
    for url in urls:
        # Make a GET request to the URL and get the response content as text
        response = requests.get(url)
        text = response.text

        # Split the text into lines and add the unique lines to the set
        for line in text.split("\n"):
            if len(line)>8:unique_lines.add(line)
            
    # Convert the set of unique lines back to a list and sort it
    sorted_lines = sorted(list(unique_lines))

    # Write the sorted lines to the output file
    with open(output_file_path, "w") as output_file:
        output_file.write("\n".join(sorted_lines))
