import requests
import pandas as pd
from supabase import create_client, Client
import os
import csv 

ALPHAVANTAGE_API_KEY = '409HR7EQNP9WGW3A'
supabase_Url = 'https://xsujstzsbguabmmfdoww.supabase.co'
supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhzdWpzdHpzYmd1YWJtbWZkb3d3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjgyODg5MzEsImV4cCI6MjA0Mzg2NDkzMX0.yl_1pRMfQtCcXASs9KVt2snmHkiamGXML24VnLeXKaI'
supabase: Client = create_client(supabase_Url, supabase_key)

def get_stock_data_daily(symbol):
    base_url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_DAILY',  
        'symbol': symbol, 
        'apikey': ALPHAVANTAGE_API_KEY,
        'outputsize': 'full'  
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    return data


nse_symbols = ['INFY']  # Have to write the code to fetch all the different symbols

data = [['Date' , 'Opening Value' , 'High' , 'Low' , 'SecurityID']]


for symbol in nse_symbols:
    print(f"Fetching data for {symbol}...")
    stock_data = get_stock_data_daily(symbol)
    
    time_series = stock_data['Time Series (Daily)']

    for key,value in time_series.items():
        ts_opening_value = value['1. open']
        ts_date = key
        ts_high = value['2. high']
        ts_low = value['3. low']
        data.append([ts_date, ts_opening_value , ts_high , ts_low , symbol])
        print(f"Date : {ts_date} , Opening Value : {ts_opening_value} , High : {ts_high} , Low : {ts_low} , Symbol : {symbol}")

    with open('stock_data_daily.csv', mode='w', newline='') as file:
        writer = csv.writer(file)    
        writer.writerows(data)
    print("CSV file created successfully!")

    data = []
#--------------------------------------------------------------------------------------------------------------------
    df = pd.read_csv('stock_data_daily.csv')
    data = df.to_dict(orient='records')
    response = supabase.table('EQUITY_PRICES').insert(data).execute()

    if response.data:
        print(f"All rows successfully entered")
    else:
        print(f"Failed to insert row . Error: {response.json()}")

    print(f"Inserted Data for {symbol}")
