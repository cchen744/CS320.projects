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
        self.dates = re.findall(r'[1-2]\d{3}-\d{2}-\d{2}', html)
        self.sic = re.findall(r"SIC=(\d+)",html)
        self.addresses = []
        self.find_address(html)
                
    def state(self):
        states = []
        for address in self.addresses:
            states.extend(re.findall(r'[A-Z]{2} \d{5}',address))
        return states
    
    def find_address(self,html):
        for addr_html in re.findall(r'<div class="mailer">([\s\S]+?)</div>', html):
            lines = []
            for line in re.findall(r'<span class="mailerAddress">([\s\S]+?)</span>', addr_html):
                lines.append(line.strip())
            self.addresses.append(("\n".join(lines)))
                
    
   