import socket
import requests

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception as e:
        local_ip = "Unable to determine local IP"
    finally:
        s.close()
    return local_ip

def get_public_ip():
    try:
        public_ip = requests.get("").text
    except Exception as e:
        public_ip = "Unable to determine public IP"
    return public_ip

if __name__ == "__main__":
    print("Local IP Address:", get_local_ip())
    print("Public IP Address:", get_public_ip())
