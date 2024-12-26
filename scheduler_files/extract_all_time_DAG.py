from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from datetime import timedelta
import subprocess

def run_script_1():
    subprocess.run(["python3", "/home/kedar/securities_project/securities_project/src/extract_data_all_time.py"], check=True)



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
    start_date=datetime(2024, 12, 23),
    catchup=False,
) as dag:

    task1 = PythonOperator(
        task_id='extract_all_time_daily_data',
        python_callable=run_script_1,
    )


    task1
