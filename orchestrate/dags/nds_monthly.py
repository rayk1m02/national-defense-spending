import os
from datetime import timedelta

import pendulum
from airflow.sdk import DAG
from airflow.providers.smtp.notifications.smtp import SmtpNotifier
from airflow.providers.standard.operators.bash import BashOperator

REPO = "/opt/nds"
DBT = "/home/airflow/dbt-venv/bin/dbt"

ALERT_EMAIL = os.environ["ALERT_EMAIL"]

failure_email = SmtpNotifier(
    from_email=ALERT_EMAIL,
    to=ALERT_EMAIL,
    subject="[nds] {{ dag.dag_id }}.{{ ti.task_id }} failed",
    html_content="Error: {{ exception }}<br>Log: {{ ti.log_url }}",
)

with DAG(
    dag_id="nds_monthly",
    schedule="0 6 15 * *", # min, hr, day of month, month, day of week
    start_date=pendulum.datetime(2026, 10, 1, tz="America/Chicago"), # pendulum handles timezones
    catchup=False, # don't go back and run every month since start_date, just run only the latest missed month once next time
    max_active_runs=1, # never run two runs at the same time
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=15),
        "on_failure_callback": failure_email,
    },
) as dag:

    # return a list of four tasks
    extracts = [
        BashOperator(
            task_id=f"extract_{source}",
            bash_command=f"cd {REPO} && python -m extract --source {source}",
        )
        for source in ["dod", "doe", "dhs", "dot"]
    ]

    load = BashOperator(
        task_id="load",
        bash_command=f"cd {REPO} && python -m load",
    )

    # dbt deps installs packages, dbt build runs and tests every model
    # dotenv gets the Redshift settings
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"cd {REPO}/transform && dotenv -f ../.env run -- {DBT} deps && dotenv -f ../.env run -- {DBT} build",
    )

    extracts >> load >> dbt_build