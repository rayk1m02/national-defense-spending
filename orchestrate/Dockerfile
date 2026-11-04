# Dockerfile builds custom Airflow image with our pipeline's Python packages installed in it

# Start from the official Airflow image on Python 3.13
FROM apache/airflow:3.3.2-python3.13

# Copy our requirement files into image. (Build context is the repo root)
COPY requirements.txt requirements-dbt.txt /tmp/

# install extract/load packages into Airflow's Python. Pin Airflow to the image's version so pip can't change it
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /tmp/requirements.txt

# create dbt separate environment and install dbt
# DAG runs dbt as /home/airflow/dbt-venv/bin/dbt
# dbt is isolated because dbt and Airflow share dependencies but often need different versions. Installing both into same Python environment can cause conflicts.
RUN python -m venv /home/airflow/dbt-venv && /home/airflow/dbt-venv/bin/pip install --no-cache-dir -r /tmp/requirements-dbt.txt