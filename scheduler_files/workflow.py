from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowSkipException
from airflow.decorators import task
from datetime import datetime, timedelta
import sys
import os
# Import the main functions from your Python scripts
dag_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current DAG file
src_dir = '/home/kedar/securities_project/src'

sys.path.append(src_dir)
print(src_dir)
from create_tables import main as create_tables_main
from extract_data import main as extract_data_main
from extracting_all_sec import main as extracting_all_sec_main

# Define the DAG
default_args = {
    'owner': 'kedar',
    'depends_on_past': False,
    'start_date': datetime(2024, 11, 19),  # Set a suitable start date
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}


with DAG(
    'python_scripts_execution',
    default_args=default_args,
    description='Execute Python scripts with main functions in sequence',
    schedule='@daily',  # Manual execution
    catchup=False,
) as dag:
    @task()
    def check_if_already_run(**kwargs):
        task_instance = kwargs['ti']
        if task_instance.previous_ti and task_instance.previous_ti.state == 'success':
            raise AirflowSkipException("Task has already run successfully. Skipping execution.")

    # Task to create tables
    @task()
    def create_tables_task():
        create_tables_main()

    # Task to extract Yahoo Finance data
    @task()
    def extraction_yf_task():
        extract_data_main()

    # Task for bulk upload
    @task()
    def bulk_upload_task():
        extracting_all_sec_main()

    # Define the execution order
    check_if_already_run() >> create_tables_task() >> extraction_yf_task() >> bulk_upload_task()
