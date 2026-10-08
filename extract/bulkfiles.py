import datetime, time
import logging
import os
import requests

# date range for this project will be October 1, 2007 to Present. (USAspending API goes back to FY 2008)

logger = logging.getLogger(__name__)

LIST_URL = "https://api.usaspending.gov/api/v2/bulk_download/list_monthly_files/"

def current_fiscal_year():
    today = datetime.date.today()
    return today.year + 1 if today.month >= 10 else today.year

def list_monthly_files(agency_id, fiscal_year, attempts=5):
    for attempt in range(1, attempts+1):
        try:
            r = requests.post(
                LIST_URL,
                json={"agency": agency_id, "fiscal_year": fiscal_year, "type": "contracts"},
                timeout=30
            )
            r.raise_for_status()
            return r.json()["monthly_files"]
        except requests.exceptions.RequestException as e:
            status = getattr(e.response, "status_code", None)
            if (status is not None and status < 500) or attempt == attempts:
                raise
            logger.warning("List request failed (%s), retry %s of %s", e, attempt, attempts - 1)
            time.sleep(60 * attempt)

def select_monthly_files(source, fiscal_years):
    full_files = [] # full file per fiscal year
    delta_files = {} # delta file per agency FY(All)

    for fiscal_year in fiscal_years:
        files = list_monthly_files(source["agency_id"], fiscal_year)

        full = [f for f in files if "_Full_" in f["file_name"]]
        if len(full) == 1:
            full_files.append(full[0])
        elif len(full) > 1:
            raise ValueError(f"Multiple full files for {source['agency_id']} {fiscal_year}, {len(full)}: {[f['file_name'] for f in full]}")
        elif fiscal_year == current_fiscal_year():
            logger.warning("No full file for current fiscal year, skipping: %s %s", source["agency_id"], fiscal_year,)
        else:
            raise ValueError(f"No full files for {source['agency_id']} {fiscal_year}")

        for f in files:
            if "_Delta_" in f["file_name"]:
                delta_files[f["file_name"]] = f

    if source["has_delta_file"] and not delta_files:
        logger.warning("Agency %s expected Delta file, none found", source["agency_id"])
    if not source["has_delta_file"] and delta_files:
        logger.warning("Agency %s not expected to have Delta file, but found %s- ignoring", source["agency_id"], list(delta_files),)
        delta_files = {}

    if len(delta_files) > 1:
        raise ValueError(f"Multiple Delta files for {source['agency_id']}: {list(delta_files)}")

    return full_files, list(delta_files.values())

def download_monthly_files(url, dest, attempts=5):
    os.makedirs(os.path.dirname(dest), exist_ok=True)           # creates a folder based on the folder part of dest path
    tmp_path = dest + ".part"                                   # append path (since we process in chunks - temporary name)

    for attempt in range(1, attempts+1):
        try: 
            with requests.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(tmp_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8 * 1024 * 1024):
                        f.write(chunk)
            break
        except requests.exceptions.RequestException as e:
            status = getattr(e.response, "status_code", None)
            if (status is not None and status < 500) or (attempt == attempts):
                raise
            logger.warning("Download failed (%s), retry %s of %s", e, attempt, attempts-1)
            time.sleep(60 * attempt)

    os.replace(tmp_path, dest)
    return dest