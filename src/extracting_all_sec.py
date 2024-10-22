import yfinance as yf
from supabase import create_client, Client
import pandas as pd
import requests
import xml.etree.ElementTree as ET

xml_file_path_1 = "/home/kedar/securities_project/config/equity_names.xml"
#xml_file_path_2 = 
def upload_file_to_supabase_storage(file,bucket):
    with open(f'{file}', 'rb') as f:
        res = supabase.storage.from_bucket(f'{bucket}').upload(f'{file}', f)
        print("Stored procedure uploaded successfully !!!")


def parse_xml_config_and_create_table(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    db_url = root.find("./database/url").text
    api_key = root.find("./database/api_key").text
    local_csv_path = root.find("./local_csv_path").text
    table_name = root.find("./table_config/name").text
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
    supabase: Client = create_client(db_url, api_key)
    print("CLIENT SUCCESSFULLY CREATED")

    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
    for field_name , field_type in fields:
        field_name = f"\"{field_name}\""
        create_table_sql += f"    {field_name} {field_type},\n"
    create_table_sql = create_table_sql.rstrip(',\n') + "\n);"  
    with open("/home/kedar/securities_project/sql_files/EQUITY_INFO.sql", "w") as sql_file:
        sql_file.write(create_table_sql)
    try:
        response = supabase.table("EQUITY_PRICES").select("*").execute()
        print(response)
    except Exception as e:
        print(f"Failed to create table: {e}")

    
    return db_url, api_key, local_csv_path, table_name, fields

#-------------------------------------------------------------------------------------------

def read_local_csv_to_supabase_storage():
    df = pd.read_csv('/home/kedar/securities_project/data/EQUITY_L.csv' , skiprows=1, header=None)
    df.columns = ['SYMBOL', 'NAME OF COMPANY', 'SERIES', 'DATE OF LISTING', 'PAID UP VALUE', 'MARKET LOT', 'ISIN NUMBER', 'FACE VALUE']
    tickers = df['SYMBOL'].tolist()
    csv_file_path = "/home/kedar/securities_project/data/equity_data.csv"


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
        res = supabase.storage.from_('equity_data_bucket').upload("/home/kedar/securities_project/data/equity_data.csv", f , {"upsert" : "true"})
        print("File uploaded to Supabase storage")


def upload_file_to_supabase_storage(file,bucket):
    with open(f'{file}', 'rb') as f:
        res = supabase.storage.from_bucket(f'{bucket}').upload(f'{file}', f)
        print("Stored procedure uploaded successfully !!!")


# def upload_data_through_rpc_call():
#     response = supabase.rpc('import_equity_prices_from_csv').execute()
#     print("EXECUTED STORED PROCEDURE !!")
#     if response.status_code == 200:
#         print("Stored procedure executed successfully.")
#     else:
#         print(f"Error executing stored procedure: {response.json()}")


if __name__ == "__main__":
        
    #create_import_function()
    #print("test")
    #upload_data_through_rpc_call()
    upload_file_to_supabase_storage('/home/kedar/securities_project/sql_files/EQUITY_INFO.sql' , 'equity_data_bucket')
    parse_xml_config_and_create_table(xml_file_path_1)