import yfinance as yf
from supabase import create_client, Client
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import os
from io import StringIO
import psycopg2
from psycopg2 import sql
from datetime import datetime
from create_tables import create_supabase_client
xml_file_path_1 = "/home/kedar/securities_project/securities_project/config/equity_names.xml"
xml_file_path_2 = "/home/kedar/securities_project/securities_project/config/equity_prices.xml"
user = "postgres.xsujstzsbguabmmfdoww"
#---------------------TO BE USED FOR DATE FILENAMING----------------------------------------------------------------------
universal_path = "/home/kedar/securities_project/data/all_time_data/equity_data"
#-------------------------------------------------------------------------------------------------------------------------

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
    df = pd.read_csv('/home/kedar/securities_project/securities_project/data/trial_file.csv' , skiprows=1, header=None)
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
        current_date = datetime.now().date()
        formatted_path = f"{universal_path}/{current_date}_all_data.csv"
        res = supabase.storage.from_('equity_data_bucket').upload(formatted_path, f , {"upsert" : "true"})
        print("File uploaded to Supabase storage")

    public_url = supabase.storage.from_('equity_data_bucket').get_public_url(formatted_path)
    return public_url

def bulk_upload_public_url(xml_file_path,public_url):
    supabase= create_supabase_client(xml_file_path)
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    db_url = root.find("./database/db_url").text
    api_key = root.find("./database/api_key").text
    db_name = root.find("./database/db_name").text
    local_csv_path = root.find("./local_csv_path").text
    table_name = root.find("./table_config/name").text
    bucket = root.find("./table_config/project_bucket").text
    supabase_url = root.find("./database/db_url").text
    user = root.find("./database/user").text
    password = root.find("./database/password").text
    port = int(root.find("./database/port").text)
    host = root.find("./database/host").text
    fields = [field.attrib['name'] for field in root.findall("./table_config/fields/field")]
    try:
        # Fetch the CSV file content from the public URL
        response = requests.get(public_url)
        response.raise_for_status() 

        csv_content = response.text

        conn = psycopg2.connect(
            dbname=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            port=db_config['port']
        )
        conn.autocommit = True

        with conn.cursor() as cursor:
            # Prepare COPY query
            copy_query = f"""
            COPY {table_name} ({", ".join(columns)})
            FROM STDIN
            WITH (FORMAT csv, HEADER true)
            """

        cursor.copy_expert(copy_query, StringIO(csv_content))
        print("Data uploaded successfully!")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Ensure connection is closed
        if conn:
            conn.close()




def main():
    public_URL = daily_series_data()
    bulk_upload_public_url(xml_file_path_2,public_URL)

if __name__ == "__main__":
    main()