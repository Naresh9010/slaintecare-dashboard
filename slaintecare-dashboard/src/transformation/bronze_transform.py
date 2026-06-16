"""
bronze_transform.py
Raw → Bronze Delta Lake layer.
Schema enforcement, type casting, null handling, audit timestamps.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger
from src.ingestion.ntpf_loader import HOSPITAL_RHA_MAP, get_hospital_rha


# ── Sláintecare wait time bands (weeks) ──────────────────────────────────────
WAIT_BAND_COLS_OP = [
    "0-6 Weeks", "6-12 Weeks", "12-18 Weeks", "18-24 Weeks",
    "24-36 Weeks", "36-52 Weeks", "52+ Weeks",
]

SLAINTECARE_OP_TARGET_WEEKS  = 12
SLAINTECARE_IPDC_TARGET_WEEKS = 10


def process_ntpf_op(raw_path: str, output_path: str) -> pd.DataFrame:
    """
    Process raw NTPF Outpatient waiting list CSV into Bronze format.
    """
    logger.info(f"Processing OP waiting list: {raw_path}")

    df = pd.read_csv(raw_path)
    df.columns = df.columns.str.strip()

    # Standardise column names
    rename_map = {}
    for col in df.columns:
        col_clean = col.strip()
        if "hospital" in col_clean.lower():
            rename_map[col] = "hospital"
        elif "speciality" in col_clean.lower() or "specialty" in col_clean.lower():
            rename_map[col] = "speciality"
        elif "archive date" in col_clean.lower() or "month" in col_clean.lower():
            rename_map[col] = "archive_date"
        elif "total" in col_clean.lower():
            rename_map[col] = "total_waiting"
    df = df.rename(columns=rename_map)

    # Parse archive date
    if "archive_date" in df.columns:
        df["archive_date"] = pd.to_datetime(df["archive_date"], dayfirst=True, errors="coerce")
        df["year"]  = df["archive_date"].dt.year
        df["month"] = df["archive_date"].dt.month
        df["month_str"] = df["archive_date"].dt.strftime("%Y-%m")

    # Add RHA mapping
    if "hospital" in df.columns:
        df["rha"] = df["hospital"].apply(get_hospital_rha)

    # Numeric coercion
    if "total_waiting" in df.columns:
        df["total_waiting"] = pd.to_numeric(df["total_waiting"], errors="coerce").fillna(0).astype(int)

    # Audit columns
    df["source_file"]     = Path(raw_path).name
    df["ingestion_ts"]    = pd.Timestamp.now()
    df["data_type"]       = "OP"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    logger.info(f"  ✅ Bronze OP: {len(df):,} rows → {output_path}")
    return df


def process_synthetic_waiting_list(output_path: str) -> pd.DataFrame:
    """
    Generates Bronze-format waiting list data matching real NTPF schema.
    Used for demo when real CSVs are not downloaded.
    """
    np.random.seed(42)

    hospitals = list(HOSPITAL_RHA_MAP.keys())
    specialities = [
        "Orthopaedics", "Ophthalmology", "Dermatology", "ENT",
        "Cardiology", "Gastroenterology", "Neurology", "Urology",
        "General Surgery", "Gynaecology", "Rheumatology", "Psychiatry",
    ]

    records = []
    months = pd.date_range("2021-01", "2025-12", freq="MS")

    for month in months:
        for hospital in hospitals:
            for speciality in np.random.choice(specialities, size=4, replace=False):
                # Simulate improvement over time (Sláintecare effect)
                months_elapsed = (month.year - 2021) * 12 + month.month
                base = np.random.randint(50, 800)
                improvement = max(0.6, 1 - (0.001 * months_elapsed))

                w_0_6   = int(base * 0.30 * improvement)
                w_6_12  = int(base * 0.25 * improvement)
                w_12_18 = int(base * 0.18)
                w_18_24 = int(base * 0.12)
                w_24_36 = int(base * 0.08)
                w_36_52 = int(base * 0.05)
                w_52p   = int(base * 0.02)
                total   = w_0_6 + w_6_12 + w_12_18 + w_18_24 + w_24_36 + w_36_52 + w_52p

                records.append({
                    "archive_date":  month,
                    "month_str":     month.strftime("%Y-%m"),
                    "year":          month.year,
                    "month":         month.month,
                    "hospital":      hospital,
                    "rha":           HOSPITAL_RHA_MAP.get(hospital, "Other"),
                    "speciality":    speciality,
                    "data_type":     "OP",
                    "w_0_6":         w_0_6,
                    "w_6_12":        w_6_12,
                    "w_12_18":       w_12_18,
                    "w_18_24":       w_18_24,
                    "w_24_36":       w_24_36,
                    "w_36_52":       w_36_52,
                    "w_52_plus":     w_52p,
                    "total_waiting": total,
                    "ingestion_ts":  pd.Timestamp.now(),
                    "source_file":   "synthetic_ntpf",
                })

    df = pd.DataFrame(records)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    logger.info(f"✅ Bronze waiting list: {len(df):,} rows → {output_path}")
    return df


if __name__ == "__main__":
    logger.info("=== Bronze Layer: Raw → Structured ===")
    df = process_synthetic_waiting_list("data/bronze/waiting_list.parquet")
    logger.info(f"   Hospitals: {df['hospital'].nunique()}")
    logger.info(f"   Months: {df['month_str'].nunique()}")
    logger.info(f"   Specialities: {df['speciality'].nunique()}")
    logger.info("=== Bronze Layer Complete ✅ ===")
