import yfinance as yf
from supabase import create_client, Client
import pandas as pd

supabase_Url = 'https://xsujstzsbguabmmfdoww.supabase.co'
supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhzdWpzdHpzYmd1YWJtbWZkb3d3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjgyODg5MzEsImV4cCI6MjA0Mzg2NDkzMX0.yl_1pRMfQtCcXASs9KVt2snmHkiamGXML24VnLeXKaI'
supabase: Client = create_client(supabase_Url, supabase_key)


df = pd.read_csv('EQUITY_L.csv' , skiprows=1, header=None)
df.columns = ['SYMBOL', 'NAME OF COMPANY', 'SERIES', 'DATE OF LISTING', 'PAID UP VALUE', 'MARKET LOT', 'ISIN NUMBER', 'FACE VALUE']
tickers = df['SYMBOL'].tolist()
csv_file_path = "equity_data.csv"


print(tickers)
all_data = pd.DataFrame()

with open(csv_file_path, 'w') as f:
    pass 

for i,ticker_symbol in enumerate(tickers):
    data = yf.Ticker(ticker_symbol)
    historical_data = data.history(period="max").reset_index()
    historical_data['ticker'] = ticker_symbol
    if i == 0:
        historical_data.to_csv(csv_file_path, index=False, mode='w', header=True)
    else:
        historical_data.to_csv(csv_file_path, index=False, mode='a', header=False)

    print(f"Data for stock {ticker_symbol} successfully added to CSV")

print("CSV CONSTRUCTED SUCCESSFULLY !!!!")

with open(csv_file_path, 'rb') as f:
    res = supabase.storage.from_('equity_data_bucket').upload("equity_data.csv", f , {"upsert" : "true"})
    print("File uploaded to Supabase storage")

