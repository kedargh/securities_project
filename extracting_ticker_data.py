import requests
import pandas as pd
from supabase import create_client, Client
import os
import csv 

supabase_Url = 'https://xsujstzsbguabmmfdoww.supabase.co'
supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhzdWpzdHpzYmd1YWJtbWZkb3d3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjgyODg5MzEsImV4cCI6MjA0Mzg2NDkzMX0.yl_1pRMfQtCcXASs9KVt2snmHkiamGXML24VnLeXKaI'
supabase: Client = create_client(supabase_Url, supabase_key)


df = pd.read_csv('EQUITY_L.csv', skiprows = 1, header = None)
df.columns = ['SYMBOL', 'NAME OF COMPANY', 'SERIES', 'DATE OF LISTING', 'PAID UP VALUE', 'MARKET LOT', 'ISIN NUMBER', 'FACE VALUE']

data = df.to_dict(orient='records')

response = supabase.table('EQUITY_INFO').insert(data).execute()

if response.data:
    print(f"All rows successfully entered")
else:
    print(f"Failed to insert row . Error: {response.json()}")
