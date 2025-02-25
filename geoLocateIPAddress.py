import requests
import json
import argparse
from datetime import datetime

def get_ip_info(ip_address=None):
    
    url = "https://ipinfo.io"
    

    if ip_address:
        url = f"{url}/{ip_address}"
    

    url = f"{url}/json"
    

    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Request failed with status code: {response.status_code}"}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Request exception: {str(e)}"}

def display_ip_info(ip_data):

    if "error" in ip_data:
        print(f"Error: {ip_data['error']}")
        return
    
    print("\n===== IP Geolocation Information =====")
    print(f"IP Address: {ip_data.get('ip', 'N/A')}")
    print(f"Hostname: {ip_data.get('hostname', 'N/A')}")
    print(f"City: {ip_data.get('city', 'N/A')}")
    print(f"Region: {ip_data.get('region', 'N/A')}")
    print(f"Country: {ip_data.get('country', 'N/A')}")
    print(f"Location: {ip_data.get('loc', 'N/A')}")
    
    loc = ip_data.get('loc')
    if loc and ',' in loc:
        lat, lng = loc.split(',')
        print(f"  - Latitude: {lat}")
        print(f"  - Longitude: {lng}")
        
    print(f"Organization: {ip_data.get('org', 'N/A')}")
    print(f"Postal Code: {ip_data.get('postal', 'N/A')}")
    print(f"Timezone: {ip_data.get('timezone', 'N/A')}")
    
    timezone = ip_data.get('timezone')
    if timezone:
        try:
            from datetime import datetime
            import pytz
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
            print(f"  - Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        except ImportError:
            print("  - Install 'pytz' package to see current time in this timezone")
        except Exception as e:
            print(f"  - Could not determine current time: {str(e)}")
    
    print("=====================================\n")

def save_to_file(ip_data, filename=None):
    if filename is None:
        ip = ip_data.get('ip', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"ip_info_{ip}_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(ip_data, f, indent=4)
        print(f"Information saved to {filename}")
    except Exception as e:
        print(f"Error saving to file: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Get geolocation information for an IP address.')
    parser.add_argument('ip', nargs='?', help='IP address to look up (default: your current IP)')
    parser.add_argument('-s', '--save', action='store_true', help='Save the information to a JSON file')
    parser.add_argument('-f', '--file', help='Specify a filename to save to')
    
    args = parser.parse_args()
    
    ip_data = get_ip_info(args.ip)
    
    display_ip_info(ip_data)
    
    if args.save or args.file:
        save_to_file(ip_data, args.file)

if __name__ == "__main__":
    main()