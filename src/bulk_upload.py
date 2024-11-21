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
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

def bulk_upload(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    db_url = root.find("./database/db_url").text
    api_key = root.find("./database/api_key").text
    file_path = root.find("./local_csv_path").text
    bucket = root.find("./database/bucket").text
    table_name = root.find("./table_config/name").text
    #print(table_name)
    supabase: Client = create_client(db_url,api_key)
    df = pd.read_csv(file_path)
    #print(df.head())
    cleaned_data = [{k.strip(): v for k, v in record.items()} for record in df.to_dict(orient="records")]
    print(cleaned_data[1])
    print("CONVERTED TO RECORDS")
    try:
        response = supabase.table(table_name).insert(cleaned_data).execute()
    except Exception as e:
        print("Error during upload:", e)

def main():
    bulk_upload(xml_file_path_1)
    bulk_upload(xml_file_path_2)
    
if __name__ == "__main__":
    main()
