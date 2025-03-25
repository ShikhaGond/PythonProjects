import re
import socket
import subprocess
import sys
import requests
from urllib.parse import urlparse

class AdBlocker:
    def __init__(self, hosts_path=None):
        """
        Initialize AdBlocker with configurable hosts file path.
        
        Args:
            hosts_path (str, optional): Path to hosts file. 
                Defaults to system-specific location.
        """
        # Detect operating system and set default hosts path
        if sys.platform.startswith('win'):
            self.hosts_path = hosts_path or r'C:\Windows\System32\drivers\etc\hosts'
        elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            self.hosts_path = hosts_path or '/etc/hosts'
        else:
            raise OSError("Unsupported operating system")
        
        # Lists for blocking
        self.ad_domains = set()
        self.block_lists = [
            'https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts',
            'https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext'
        ]

    def fetch_blocklist(self):
        """
        Fetch ad blocking lists from multiple sources.
        
        Returns:
            set: Unique ad domains to block
        """
        ad_domains = set()
        
        for url in self.block_lists:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # Extract domains from hosts file format
                    domains = re.findall(r'0\.0\.0\.0\s+([^\s]+)', response.text)
                    ad_domains.update(domains)
            except Exception as e:
                print(f"Error fetching blocklist from {url}: {e}")
        
        return ad_domains

    def update_hosts_file(self):
        """
        Update system hosts file to block ad domains.
        Requires administrative/root privileges.
        """
        # Fetch ad domains
        self.ad_domains = self.fetch_blocklist()
        
        # Create blocked domains entries
        block_entries = [f"0.0.0.0 {domain}\n" for domain in self.ad_domains]
        
        try:
            # Read existing hosts file
            with open(self.hosts_path, 'r') as f:
                existing_content = f.readlines()
            
            # Remove previous ad blocking entries
            cleaned_content = [
                line for line in existing_content 
                if not line.strip().startswith('0.0.0.0') or 'ad' not in line
            ]
            
            # Append new block entries
            with open(self.hosts_path, 'w') as f:
                f.writelines(cleaned_content)
                f.writelines(block_entries)
            
            print(f"Updated hosts file with {len(block_entries)} ad domains")
        except PermissionError:
            print("Administrative privileges required to modify hosts file.")
            self._request_admin_rights()

    def _request_admin_rights(self):
        """
        Request administrative rights based on operating system.
        """
        if sys.platform.startswith('win'):
            # Windows: Use runas
            subprocess.run(['runas', '/user:Administrator', 'python', sys.argv[0]])
        elif sys.platform.startswith('linux'):
            # Linux: Use sudo
            subprocess.run(['sudo', 'python3', sys.argv[0]])
        elif sys.platform.startswith('darwin'):
            # macOS: Use sudo
            subprocess.run(['sudo', 'python3', sys.argv[0]])

    def is_ad_domain(self, url):
        """
        Check if a given URL is an ad domain.
        
        Args:
            url (str): URL to check
        
        Returns:
            bool: True if ad domain, False otherwise
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Check against blocklist
        return any(ad_domain in domain for ad_domain in self.ad_domains)

    def block_network_ads(self):
        """
        Implement network-level ad blocking using socket filtering.
        """
        def hook_socket():
            """
            Modify socket connection to block ad domains.
            """
            original_socket = socket.socket
            
            def new_socket(*args, **kwargs):
                sock = original_socket(*args, **kwargs)
                
                def connect(addr):
                    hostname = addr[0]
                    if self.is_ad_domain(f'http://{hostname}'):
                        print(f"Blocked connection to ad domain: {hostname}")
                        return
                    return original_connect(addr)
                
                original_connect = sock.connect
                sock.connect = connect
                return sock
            
            socket.socket = new_socket

        hook_socket()

    def generate_report(self):
        """
        Generate a report of blocked ad domains.
        
        Returns:
            dict: Report of ad blocking statistics
        """
        return {
            'total_domains_blocked': len(self.ad_domains),
            'block_lists_used': self.block_lists
        }

def main():
    # Initialize ad blocker
    ad_blocker = AdBlocker()
    
    # Update hosts file
    ad_blocker.update_hosts_file()
    
    # Enable network-level ad blocking
    ad_blocker.block_network_ads()
    
    # Generate and print blocking report
    report = ad_blocker.generate_report()
    print("\nAd Blocking Report:")
    for key, value in report.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()