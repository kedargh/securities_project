from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from datetime import timedelta
import subprocess

def run_script_1():
    subprocess.run(["python3", "/home/kedar/securities_project/securities_project/src/extract_data_daily.py"], check=True)

def run_script_2():
    subprocess.run(["python3" , "/home/kedar/securities_project/securities_project/src/daily_data_upload.py"] , check=True)



default_args = {
    'owner': 'kedar',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}


with DAG(
    'scripts_dag',
    default_args=default_args,
    description='A DAG to run 3 scripts',
    schedule='@daily',
    start_date=datetime(2024, 11, 18),
    catchup=False,
) as dag:

    task1 = PythonOperator(
        task_id='create_tables',
        python_callable=run_script_1,
    )

    task2 = PythonOperator(
        task_id='extract_all_time_data',
        python_callable=run_script_2,
    )


    task1 >> task2  
