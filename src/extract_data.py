import yfinance as yf
from supabase import create_client, Client
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import os
import psycopg2
xml_file_path_1 = "/home/kedar/securities_project/securities_project/config/equity_names.xml"
xml_file_path_2 = "/home/kedar/securities_project/securities_project/config/equity_prices.xml"
user = "postgres.xsujstzsbguabmmfdoww"


def create_supabase_client(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    db_url = root.find("./database/db_url").text
    api_key =  root.find("./database/api_key").text
    supabase: Client = create_client(db_url , api_key)
    return(supabase)

def establish_connection(SUPABASE_URL , SUPABASE_DB , SUPABASE_USER , SUPABASE_PASSWORD , PORT):
        CONNECTION = psycopg2.connect(host = SUPABASE_URL, dbname = SUPABASE_DB, user = SUPABASE_USER, password = SUPABASE_PASSWORD , sslmode = "require") 
        CURSOR = CONNECTION.cursor()
        return CURSOR,CONNECTION  

def execute_any_query(query , SUPABASE_URL , SUPABASE_DB , SUPABASE_USER , SUPABASE_PASSWORD , PORT):
    CURSOR, CONNECTION = None, None
    try:
        CURSOR,CONNECTION = establish_connection(SUPABASE_URL , SUPABASE_DB , SUPABASE_USER , SUPABASE_PASSWORD , PORT)  
        CURSOR.execute(query)
        CONNECTION.commit()
    except Exception as e:
        print("ERROR : " , e)
    finally:
        if CURSOR:
            CURSOR.close()

#-----------------------------------------------------------------------------------------------------------------------------------------------

def daily_series_data():
    df = pd.read_csv('/home/kedar/securities_project/securities_project/data/EQUITY_L.csv' , skiprows=1, header=None)
    df.columns = ['SYMBOL', 'NAME OF COMPANY', 'SERIES', 'DATE OF LISTING', 'PAID UP VALUE', 'MARKET LOT', 'ISIN NUMBER', 'FACE VALUE']
    tickers = df['SYMBOL'].tolist()
    csv_file_path = "/home/kedar/securities_project/securities_project/data/equity_data.csv"
    supabase = create_supabase_client(xml_file_path_1)
    no_data_tickers = []
    print(tickers)

    i = 0
    for ticker in tickers:
        data = yf.Ticker(ticker)
        historical_data = data.history(period="max").reset_index()
        if historical_data.empty:
            no_data_tickers.append(ticker)
        else:
            selected_data = historical_data[["Date","Open","High","Low","Close","Volume","Dividends","Stock Splits"]]
            selected_data['ticker'] = ticker
            if i == 0:
                selected_data.to_csv(csv_file_path, index=False, mode='w', header=True)
            else:
                selected_data.to_csv(csv_file_path, index=False, mode='a', header=False)
            i += 1

            print(f"Data for stock {ticker} successfully added to CSV")

    print("CSV CONSTRUCTED SUCCESSFULLY !!!!")
    print(no_data_tickers)

    with open(csv_file_path, 'rb') as f:
        res = supabase.storage.from_('equity_data_bucket').upload("/home/kedar/securities_project/data/equity_data.csv", f , {"upsert" : "true"})
        print("File uploaded to Supabase storage")

def main():
    daily_series_data()

# if __name__ == "__main__":
#     main()