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
def parse_xml_config_and_create_table(xml_file_path):
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
    fields = []
    for field in root.findall("./table_config/fields/field"):
        field_name = field.attrib['name']
        field_type = field.attrib['type']
        fields.append((field_name, field_type))
    print(db_url)
    print(api_key)
    print(local_csv_path)
    print(table_name)
    print(fields)
    print(bucket)

    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
    for field_name , field_type in fields:
        field_name = f"\"{field_name}\""
        create_table_sql += f"    {field_name} {field_type},\n"
    create_table_sql = create_table_sql.rstrip(',\n') + "\n);"  
    print(create_table_sql)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    with open(f"/home/kedar/securities_project/securities_project/sql_files/{table_name}.sql", "w") as sql_file:
        sql_file.write(create_table_sql)
        print("WRITTEN QUERY TO FILE !!!")
    
    execute_any_query(create_table_sql , host , db_name , user , password , port)

    with open(f"/home/kedar/securities_project/securities_project/sql_files/{table_name}.sql", 'rb') as upload_file:
        file_name = os.path.basename(upload_file.name)
        res = supabase.storage.from_('equity_data_bucket').upload(file = upload_file,path=f"create_table_files/{file_name}", file_options={"upsert" : "true"})
        print("File uploaded to Supabase storage")
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

def daily_series_data():
    df = pd.read_csv('/home/kedar/securities_project/securities_project/data/equity_list.csv' , skiprows=1, header=None)
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

if __name__ == "__main__":
    parse_xml_config_and_create_table(xml_file_path_1)
    #parse_xml_config_and_create_table(xml_file_path_2)
    #daily_series_data()
    bulk_upload(xml_file_path_1)
    #bulk_upload(xml_file_path_2)
