import pandas as pd
import re
import netaddr
from bisect import bisect

ips = pd.read_csv("ip2location.csv")

# def lookup_region(ip):
#     ip = re.sub(r'[A-Za-z]', '0', ip)
#     idx = bisect(ips['low'],int(netaddr.IPAddress(ip)))
#     region = ips.iloc[idx-1]['region']
#     return region

# Convert to list for faster access (assumes 'low' column is sorted)
low_bounds = ips['low'].tolist()
regions = ips['region'].tolist()

# Create a cache to store previously looked-up results
region_cache = {}

def lookup_region(ip):
    # If we've already seen this IP, return cached result
    if ip in region_cache:
        return region_cache[ip]
    
    # Sanitize IP if it's anonymized
    ip_clean = re.sub(r'[A-Za-z]', '0', ip)
    ip_int = int(netaddr.IPAddress(ip_clean))

    # Binary search for region
    idx = bisect(low_bounds, ip_int)
    region = regions[idx - 1] if idx > 0 else "Unknown"

    # Cache and return
    region_cache[ip] = region
    return region

class Filing:
    def __init__(self, html):
        # self.dates = re.findall(r'([1-2]\d{3}-\d{2})-(0[1-9]|[12][0-9]|3[01])', html)
        self.dates = re.findall(r'(?:19|20)\d{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])',html)
        self.sic = 0
        self.find_sic(html)
        self.addresses = []
        self.find_address(html)
                
    def state(self):
        # states = []
        for address in self.addresses:
            current_state = (re.findall(r'\W([A-Z]{2})\s*\d{5}',address))
            if current_state !=[] and len(current_state)==1:
                return(''.join(current_state))
            elif current_state != []:
                return(current_state)
        return None
    
    def find_sic(self,html):
        match = re.search(r"SIC=(\d{4})", html)
        self.sic = int(match.group(1)) if match else None
    
    
    def find_address(self,html):
        for addr_html in re.findall(r'<div class="mailer">([\s\S]+?)</div>', html):
            lines = []
            for line in re.findall(r'<span class="mailerAddress">([\s\S]+?)</span>', addr_html):
                lines.append(line.strip())
            if ("\n".join(lines)) != '':
                self.addresses.append(("\n".join(lines)))
                
    
   