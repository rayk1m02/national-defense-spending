import os
import logging

from extract.bulkfiles import current_fiscal_year, select_monthly_files, download_monthly_files
from extract.storage import get_client, build_key, exists, has_objects, upload
from extract.prestage import prestage
from extract.settings import DOWNLOAD_DIR, FIRST_FISCAL_YEAR
from extract.sources import SOURCES

def is_loaded(client, name, file, raw_key, prestaged_key):
    if file["fiscal_year"] is None:                                                                                                     # delta (each month's new data)
        return exists(client, raw_key) and exists(client, prestaged_key)
    return (has_objects(client, build_key("raw", name, file, "")) and has_objects(client, build_key("prestaged", name, file, "")))      # full (one file per fiscal year)

def run_extract(fiscal_years, source_names=None):
    client = get_client()

    for name, source in SOURCES.items():
        if source_names and name not in source_names:                   # if given a source param, only run for those values
            continue
        full, delta = select_monthly_files(source, fiscal_years)

        for file in full + delta:
            raw_key = build_key("raw", name, file, file["file_name"])
            csv_name = file["file_name"].replace(".zip", ".csv")
            prestaged_key = build_key("prestaged", name, file, csv_name)

            if is_loaded(client, name, file, raw_key, prestaged_key):
                continue
           
            dest = os.path.join(DOWNLOAD_DIR, name, file["file_name"])  # downloads\dod\FY2025_097_Contracts_Full_20260906.zip
            zip_path = download_monthly_files(file["url"], dest)
            if not exists(client, raw_key):                             # in the case that raw_key exists but prestage_key upload failed previously
                upload(client, zip_path, raw_key)
            csv_path = prestage(zip_path, source)
            upload(client, csv_path, prestaged_key)
           
            os.remove(zip_path)
            os.remove(csv_path)

logging.basicConfig(level=logging.INFO)
run_extract(range(FIRST_FISCAL_YEAR, current_fiscal_year()+1))
#run_extract(range(2025, 2026), source_names=["doe"])