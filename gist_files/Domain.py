import socket

# List of domain names
domain_names = ["youtube.com", "google.com", "github.com"]

# Function to resolve and print IP addresses for domain names
def print_ip_addresses(domain_names):
    for domain in domain_names:
        try:
            ip_address = socket.gethostbyname(domain)
            print(f"Domain: {domain}, IP Address: {ip_address}")
        except socket.error as e:
            print(f"Unable to resolve IP address for {domain}: {str(e)}")

# Call the function with your list of domain names
print_ip_addresses(domain_names)
