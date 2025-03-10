from airflow import DAG
# from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 0,
}

with DAG(
    'crawl_tgju',
    default_args=default_args,
    schedule_interval='*/5 * * * *',  # Adjust as needed
    catchup=False
) as dag_tgju:
    # crawl_tgju = BashOperator(
    #     task_id='crawl_tgju',
    #     bash_command="cd /app && docker compose run --rm crawl-tgju",
    # )
    crawl_tgju = BashOperator(
        task_id='crawl_tgju',
        bash_command="docker run --rm --network=adb-project_backend adb-project-crawl-tgju python crawl.py",
    )
    # crawl_tgju = BashOperator(
    #     task_id='crawl_tgju',
    #     bash_command="cd /opt/airflow/dags/crawl_tgju/ && python crawl.py",
    # )
