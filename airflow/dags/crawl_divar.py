from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 0,
}

with DAG(
    'crawl_divar',
    default_args=default_args,
    schedule_interval='@hourly',  # Adjust as needed
    catchup=False
) as dag_divar:
    # crawl_divar = DockerOperator(
    #     task_id='crawl_divar',
    #     image='crawl-divar',  # Must match your service name in docker-compose
    #     container_name='crawl-divar',
    #     api_version='auto',
    #     auto_remove="never",
    #     command="python crawl.py",
    #     docker_url="unix://var/run/docker.sock",
    #     network_mode="backend",
    # )
    crawl_tgju = BashOperator(
        task_id='crawl_divar',
        bash_command="docker run --rm --network=adb-project_backend adb-project-crawl-divar python crawl.py",
    )
    # crawl_divar = BashOperator(
    #     task_id='crawl_divar',
    #     bash_command="cd /opt/airflow/dags/crawl_divar/ && python crawl.py",
    # )