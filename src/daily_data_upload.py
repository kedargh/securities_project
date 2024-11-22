import yfinance as yf
from supabase import create_client, Client
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import os
import psycopg2
from bulk_upload import bulk_upload

xml_file_path = "/home/kedar/securities_project/securities_project/config/equity_prices.xml"
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

#--------------------------------------------------------------------------------------------------------------------------------------------

def upload_todays_data(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    db_url = root.find("./database/db_url").text
    api_key = root.find("./database/api_key").text
    file_path = root.find("./local_csv_path_daily").text
    bucket = root.find("./database/bucket").text
    table_name = root.find("./table_config/name").text
    supabase: Client = create_client(db_url,api_key)
    df = pd.read_csv(file_path)
    cleaned_data = [{k.strip(): v for k, v in record.items()} for record in df.to_dict(orient="records")]
    print(cleaned_data[1])
    print("CONVERTED TO RECORDS")
    try:
        response = supabase.table(table_name).insert(cleaned_data).execute()
    except Exception as e:
        print("Error during upload:", e)


def main():
    upload_todays_data(xml_file_path)

        
if __name__ == "__main__":
    main()