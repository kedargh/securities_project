import yfinance as yf
from supabase import create_client, Client
import pandas as pd
import requests
#from airflow import DAG
# from airflow.operators.python_operator import PythonOperator
# from datetime import datetime, timedelta

supabase_Url = 'https://xsujstzsbguabmmfdoww.supabase.co'
supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhzdWpzdHpzYmd1YWJtbWZkb3d3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjgyODg5MzEsImV4cCI6MjA0Mzg2NDkzMX0.yl_1pRMfQtCcXASs9KVt2snmHkiamGXML24VnLeXKaI'
supabase: Client = create_client(supabase_Url, supabase_key)


# default_args = {
#     'owner': 'kedar',  # Your name
#     'depends_on_past': False,
#     'start_date': datetime(2024, 10, 14),  
#     'email_on_failure': False,
#     'email_on_retry': False,
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5),
# }

# dag = DAG(
#     'yfinance_supabase_eod_job',
#     default_args=default_args,
#     description='A DAG to fetch stock data from Yahoo Finance and upload to Supabase daily',
#     schedule_interval='59 23 * * *',  
# )


def read_local_csv_to_supabase_storage():
    df = pd.read_csv('EQUITY_L.csv' , skiprows=1, header=None)
    df.columns = ['SYMBOL', 'NAME OF COMPANY', 'SERIES', 'DATE OF LISTING', 'PAID UP VALUE', 'MARKET LOT', 'ISIN NUMBER', 'FACE VALUE']
    tickers = df['SYMBOL'].tolist()
    csv_file_path = "equity_data.csv"


    print(tickers)
    all_data = pd.DataFrame()
    no_data_tickers = []
    with open(csv_file_path, 'w') as f:
        pass 

    for i,ticker_symbol in enumerate(tickers):
        data = yf.Ticker(ticker_symbol)
        historical_data = data.history(period="max").reset_index()
        if historical_data.empty:
            no_data_tickers.append(ticker_symbol)
            print(f"No data available for stock {ticker_symbol}")
            continue
        
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


def create_import_function():
    with open('sql_files/import_equity_prices_from_csv.sql', 'rb') as f:
        res = supabase.storage.from_('equity_data_bucket').upload('import_equity_prices_from_csv.sql', f)
        print("Stored procedure uploaded successfully !!!")


def upload_data_through_rpc_call():
    response = supabase.rpc('import_equity_prices_from_csv').execute()
    print("EXECUTED STORED PROCEDURE !!")
    if response.status_code == 200:
        print("Stored procedure executed successfully.")
    else:
        print(f"Error executing stored procedure: {response.json()}")


if __name__ == "__main__":
    #create_import_function()
    #print("test")
    #upload_data_through_rpc_call()
