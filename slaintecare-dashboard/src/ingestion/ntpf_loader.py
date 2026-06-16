"""
ntpf_loader.py
Downloads real NTPF waiting list open data CSVs from ntpf.ie
and saves them to the local raw data folder and optionally S3.

Data source: https://www.ntpf.ie/waiting-list-data/open-data/
Updated monthly by the National Treatment Purchase Fund.
Licence: Open Government Licence (Ireland)
"""

import requests
import os
import yaml
from pathlib import Path
from loguru import logger


# ── Real NTPF Open Data URLs ──────────────────────────────────────────────────
# Source: https://www.ntpf.ie/waiting-list-data/open-data/

NTPF_DATASETS = {
    "op_by_hospital": {
        "url_template": "https://www.ntpf.ie/home/OpenData/OP%20Waiting%20List%20By%20Hospital%20{year}.csv",
        "description": "Outpatient Waiting List by Hospital",
        "years": [2021, 2022, 2023, 2024, 2025, 2026],
    },
    "ipdc_by_hospital": {
        "url_template": "https://www.ntpf.ie/home/OpenData/IPDC%20Waiting%20List%20By%20Hospital%20{year}.csv",
        "description": "Inpatient/Day Case Waiting List by Hospital",
        "years": [2021, 2022, 2023, 2024, 2025, 2026],
    },
    "op_by_speciality": {
        "url_template": "https://www.ntpf.ie/home/OpenData/OP%20Waiting%20List%20By%20Speciality%20{year}.csv",
        "description": "Outpatient Waiting List by Speciality",
        "years": [2021, 2022, 2023, 2024, 2025, 2026],
    },
    "gi_endoscopy": {
        "url_template": "https://www.ntpf.ie/home/OpenData/GI%20Endoscopy%20Waiting%20List%20By%20Hospital%20{year}.csv",
        "description": "GI Endoscopy Waiting List by Hospital",
        "years": [2021, 2022, 2023, 2024, 2025, 2026],
    },
}

# ── Hospital → Regional Health Area mapping ───────────────────────────────────
# Based on HSE's 6 Regional Health Areas (Sláintecare reform structure)
HOSPITAL_RHA_MAP = {
    # Dublin & North East
    "Beaumont Hospital":                    "Dublin & North East",
    "Mater Misericordiae University Hospital": "Dublin & North East",
    "Our Lady of Lourdes Hospital Drogheda": "Dublin & North East",
    "Cavan General Hospital":              "Dublin & North East",
    "Connolly Hospital Blanchardstown":    "Dublin & North East",
    # Dublin & Midlands
    "St. Vincent's University Hospital":   "Dublin & Midlands",
    "St. James's Hospital":                "Dublin & Midlands",
    "Tallaght University Hospital":        "Dublin & Midlands",
    "Naas General Hospital":               "Dublin & Midlands",
    "Midland Regional Hospital Tullamore": "Dublin & Midlands",
    # South West
    "Cork University Hospital":            "South West",
    "Mercy University Hospital":           "South West",
    "Kerry General Hospital":              "South West",
    "South Tipperary General Hospital":    "South West",
    # South East
    "University Hospital Waterford":       "South East",
    "Wexford General Hospital":            "South East",
    "St. Luke's General Hospital Kilkenny": "South East",
    # West
    "University Hospital Galway":          "West",
    "Mayo University Hospital":            "West",
    "Portiuncula University Hospital":     "West",
    "Sligo University Hospital":           "West",
    # Mid West
    "University Hospital Limerick":        "Mid West",
    "Ennis Hospital":                      "Mid West",
    "Nenagh Hospital":                     "Mid West",
}


def download_ntpf_data(output_dir: str = "data/raw/ntpf") -> dict:
    """
    Downloads all available NTPF open data CSVs.

    Args:
        output_dir: Local directory to save downloaded files.

    Returns:
        Dict of {dataset_key: [list of saved file paths]}
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    saved_files = {}

    for dataset_key, dataset_info in NTPF_DATASETS.items():
        saved_files[dataset_key] = []
        logger.info(f"Downloading: {dataset_info['description']}")

        for year in dataset_info["years"]:
            url = dataset_info["url_template"].format(year=year)
            filename = f"{dataset_key}_{year}.csv"
            output_path = Path(output_dir) / filename

            if output_path.exists():
                logger.info(f"  Already exists, skipping: {filename}")
                saved_files[dataset_key].append(str(output_path))
                continue

            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    size_kb = len(response.content) / 1024
                    logger.info(f"  ✅ Downloaded {filename} ({size_kb:.1f} KB)")
                    saved_files[dataset_key].append(str(output_path))
                else:
                    logger.warning(f"  ⚠️  {year} not available (HTTP {response.status_code})")
            except requests.RequestException as e:
                logger.error(f"  ❌ Failed to download {filename}: {e}")

    total = sum(len(v) for v in saved_files.values())
    logger.info(f"✅ NTPF download complete — {total} files saved to {output_dir}")
    return saved_files


def get_hospital_rha(hospital_name: str) -> str:
    """Map a hospital name to its Regional Health Area."""
    for hospital, rha in HOSPITAL_RHA_MAP.items():
        if hospital.lower() in hospital_name.lower():
            return rha
    return "Other / National"


if __name__ == "__main__":
    logger.info("=== Downloading NTPF Open Data (Real Irish Government Data) ===")
    files = download_ntpf_data()
    for dataset, paths in files.items():
        logger.info(f"  {dataset}: {len(paths)} files")
