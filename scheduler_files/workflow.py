from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowSkipException
from datetime import datetime, timedelta
import sys
import os
# Import the main functions from your Python scripts
dag_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current DAG file
src_dir = os.path.join(dag_dir, '..', '..' , 'securities_project','src')

sys.path.append(src_dir)
print(src_dir)
from create_tables import main as create_tables_main
from extract_data import main as extract_data_main
from extracting_all_sec import main as extracting_all_sec_main

# Define the DAG
default_args = {
    'owner': 'kedar',
    'depends_on_past': False,
    'start_date': datetime(2024, 11, 15),  # Set a suitable start date
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def check_if_already_run(**kwargs):
    task_instance = kwargs['ti']
    if task_instance.previous_ti and task_instance.previous_ti.state == 'success':
        raise AirflowSkipException("Task has already run successfully. Skipping execution.")

def create_tables_task():
    create_tables_main()

with DAG(
    'python_scripts_execution',
    default_args=default_args,
    description='Execute Python scripts with main functions in sequence',
    schedule_interval='@daily',  # Manual execution
    catchup=False,
) as dag:

    check_task = PythonOperator(
        task_id='check_if_already_run',
        python_callable=check_if_already_run,
        provide_context=True,
    )

    create_tables_task = PythonOperator(
        task_id='create_tables_task',
        python_callable=create_tables_task,
    )

    extraction_yf = PythonOperator(
        task_id='extract_data_task',
        python_callable=extract_data_main,   # Call the main function of script2
    )

    bulk_upload = PythonOperator(
        task_id='extracting_all_sec_task',
        python_callable=extracting_all_sec_main,  # Call the main function of script3
    )

    # Define the execution order
    check_task >> create_tables_task >> extraction_yf >> bulk_upload

