FROM apache/airflow:3.3.2-python3.13

COPY requirements.txt requirements-dbt.txt /tmp/

# install extract/load packages into Airflow's Python
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /tmp/requirements.txt

# create dbt separate environment and install dbt
# DAG runs dbt as /home/airflow/dbt-venv/bin/dbt
RUN python -m venv /home/airflow/dbt-venv \
    && /home/airflow/dbt-venv/bin/pip install --no-cache-dir -r /tmp/requirements-dbt.txt