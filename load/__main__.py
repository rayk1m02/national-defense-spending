import os

import redshift_connector
from dotenv import load_dotenv

from extract.columns import COLUMNS
from extract.settings import BUCKET, PRESTAGED_PREFIX
from extract.storage import get_client, list_keys

RAW_TABLE = "raw_nds.contract_transactions"
# temp table each file is copied into before inserting into the raw table
# COPY can only fill columns from the CSV, so each file lands here first
# source, source_file, and _loaded_at are then added on the INSERT into the raw table.
STAGE_TABLE = "stage_load"


# opens one connection / Redshift session using the settings in .env.
def connect():
    return redshift_connector.connect(
        host=os.environ["NDS_REDSHIFT_HOST"],
        port=int(os.environ["NDS_REDSHIFT_PORT"]),
        database=os.environ["NDS_REDSHIFT_DATABASE"],
        user=os.environ["NDS_REDSHIFT_USER"],
        password=os.environ["NDS_REDSHIFT_PASSWORD"],
    )


# returns the set of S3 keys that already have rows in the raw table
def loaded_files(cursor):
    cursor.execute(f"SELECT DISTINCT source_file FROM {RAW_TABLE}")
    # each row is a one item list, so row[0] is the key
    return {row[0] for row in cursor.fetchall()}


# loads one prestaged file. COPY into STAGE_TABLE then INSERT into RAW_TABLE
# we add source, source_file, and load time values for the last three columns
def load_file(conn, key):
    # "dod" from "prestaged/dod/full/..."
    source = key.split("/")[1]
    # 65 column names from csv (in order)
    columns = ", ".join(COLUMNS)
    role_arn = os.environ["NDS_REDSHIFT_COPY_ROLE_ARN"]
    cursor = conn.cursor()
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {STAGE_TABLE}")
        cursor.execute(f"CREATE TEMP TABLE {STAGE_TABLE} (LIKE {RAW_TABLE})")
        cursor.execute(f"""
            COPY {STAGE_TABLE} ({columns})
            FROM 's3://{BUCKET}/{key}'
            IAM_ROLE '{role_arn}'
            FORMAT AS CSV
            IGNOREHEADER 1
            EMPTYASNULL
        """)
        # rows loaded by the last/recent COPY in this session
        cursor.execute("SELECT pg_last_copy_count()")
        copied = cursor.fetchone()[0]
        # remove rows from earlier load of this file, so a reload does not duplicate rows
        cursor.execute(f"DELETE FROM {RAW_TABLE} WHERE source_file = '{key}'")
        cursor.execute(f"""
            INSERT INTO {RAW_TABLE}
            SELECT {columns}, '{source}', '{key}', GETDATE()
            FROM {STAGE_TABLE}
        """)
        # rows inserted
        inserted = cursor.rowcount
        # check if every copied row has been inserted
        if inserted != copied:
            raise RuntimeError(f"{key}: copied {copied} rows, inserted {inserted}")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    print(f"{key}: {inserted} rows")


def main():
    load_dotenv()
    # extract user policy only allows listing with a prefix "prestaged/*", so we append "/"
    keys = list_keys(get_client(), f"{PRESTAGED_PREFIX}/")
    conn = connect()
    try:
        done = loaded_files(conn.cursor())
        # only keys with no rows in the raw table yet
        todo = [key for key in keys if key not in done]
        print(f"{len(todo)} of {len(keys)} files to load")
        for key in todo:
            load_file(conn, key)
    finally:
        conn.close()


if __name__ == "__main__":
    main()