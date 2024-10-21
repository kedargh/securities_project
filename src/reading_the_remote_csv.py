import requests
import os
import urllib.request

csv_url = 'https://nsearchives.nseindia.com/web/sites/default/files/inline-files/CDC_Record_Date_Details_0.csv'
local_path = '/home/kedar/securities_project/src/equity_data.csv'

def download_csv(url, save_path):
    #response = requests.get(url)
    #print("URL request completed")
    fh = urllib.request.urlretrieve(csv_url, save_path)
    print(f"Downloaded and saved to {save_path}")
    html = fh.read().decode("utf8")

download_csv(csv_url, local_path)
