import requests
from bs4 import BeautifulSoup

# URL of the webpage containing the CSV file link
webpage_url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"

# Send a GET request to fetch the webpage content
response = requests.get(webpage_url, timeout=10)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the link to the CSV file (update the 'href' logic as needed)
    csv_link = soup.find('a', href=lambda href: href and href.endswith('.csv'))
    
    if csv_link:
        # Extract the full URL of the CSV file
        csv_url = csv_link['href']
        if not csv_url.startswith('http'):  # Handle relative URLs
            csv_url = requests.compat.urljoin(webpage_url, csv_url)
        
        # Download the CSV file
        csv_response = requests.get(csv_url, timeout=10)
        if csv_response.status_code == 200:
            # Save the file locally
            local_filename = "/home/kedar/securities_project/securities_project/data/EQUITY_L1.csv"
            with open(local_filename, 'wb') as file:
                file.write(csv_response.content)
            print(f"CSV file successfully downloaded as '{local_filename}'")
        else:
            print(f"Failed to download the CSV file. HTTP Status Code: {csv_response.status_code}")
    else:
        print("No CSV link found on the webpage.")
else:
    print(f"Failed to fetch the webpage. HTTP Status Code: {response.status_code}")
