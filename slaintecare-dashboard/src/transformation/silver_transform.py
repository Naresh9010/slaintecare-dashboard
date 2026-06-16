"""
silver_transform.py
Bronze → Silver layer.
Computes Sláintecare KPIs, breach flags, and target tracking.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger

SLAINTECARE_OP_TARGET_WEEKS   = 12
SLAINTECARE_IPDC_TARGET_WEEKS = 10


def build_silver_waiting_list(bronze_path: str, output_path: str) -> pd.DataFrame:
    """
    Adds Sláintecare KPI columns to the Bronze waiting list table.
    - Flags patients waiting beyond target
    - Computes % waiting > 12 months
    - Marks hospital/speciality as breaching target
    """
    logger.info("Building Silver waiting list table...")

    df = pd.read_parquet(bronze_path)

    # Patients waiting beyond Sláintecare OP target (12 weeks)
    df["waiting_beyond_target"] = (
        df["w_12_18"] + df["w_18_24"] + df["w_24_36"] + df["w_36_52"] + df["w_52_plus"]
    )

    # % waiting > 12 months
    df["pct_over_12_months"] = np.where(
        df["total_waiting"] > 0,
        (df["w_52_plus"] / df["total_waiting"] * 100).round(2),
        0
    )

    # % waiting beyond target
    df["pct_beyond_target"] = np.where(
        df["total_waiting"] > 0,
        (df["waiting_beyond_target"] / df["total_waiting"] * 100).round(2),
        0
    )

    # Target breach flag
    df["target_breached"] = df["pct_beyond_target"] > 0

    # Severity tier
    df["wait_severity"] = pd.cut(
        df["pct_beyond_target"],
        bins=[-1, 0, 20, 50, 100],
        labels=["On Target", "Moderate", "Serious", "Critical"]
    )

    # Slaintecare phase (for trend analysis)
    df["slaintecare_phase"] = pd.cut(
        df["year"],
        bins=[2020, 2021, 2022, 2023, 2024, 2025, 2026],
        labels=["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5", "Phase 6"]
    )

    df["silver_processed_at"] = pd.Timestamp.now()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    logger.info(f"✅ Silver waiting list: {len(df):,} rows → {output_path}")
    return df


def build_silver_gp_coverage(hse_raw_path: str, output_path: str,
                               population: dict = None) -> pd.DataFrame:
    """
    Computes GP Visit Card coverage KPIs per CHO and RHA.
    """
    logger.info("Building Silver GP coverage table...")

    df = pd.read_csv(hse_raw_path)

    # National population estimates per RHA (CSO 2022 Census)
    if population is None:
        population = {
            "Dublin & North East": 680000,
            "Dublin & Midlands":   610000,
            "South West":          540000,
            "South East":          330000,
            "West":                450000,
            "Mid West":            380000,
        }

    rha_pop_df = pd.DataFrame([
        {"rha": rha, "rha_population": pop}
        for rha, pop in population.items()
    ])

    # Aggregate to RHA level
    rha_df = (
        df.groupby(["month", "rha"])
        .agg(gp_visit_cards=("gp_visit_cards", "sum"))
        .reset_index()
        .merge(rha_pop_df, on="rha", how="left")
    )

    rha_df["coverage_pct"] = (rha_df["gp_visit_cards"] / rha_df["rha_population"] * 100).round(2)
    rha_df["slaintecare_target_pct"] = 100  # Universal coverage target
    rha_df["gap_to_target"] = (100 - rha_df["coverage_pct"]).round(2)
    rha_df["silver_processed_at"] = pd.Timestamp.now()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    rha_df.to_parquet(output_path, index=False)
    logger.info(f"✅ Silver GP coverage: {len(rha_df):,} rows → {output_path}")
    return rha_df


if __name__ == "__main__":
    logger.info("=== Silver Layer: KPI Computation ===")

    wl = build_silver_waiting_list(
        "data/bronze/waiting_list.parquet",
        "data/silver/waiting_list.parquet"
    )
    logger.info(f"   Target breaches: {wl['target_breached'].sum():,} / {len(wl):,} records")

    from src.ingestion.hse_loader import load_hse_data
    hse = load_hse_data()

    gp = build_silver_gp_coverage(
        "data/raw/hse/gp_visit_cards.csv",
        "data/silver/gp_coverage.parquet"
    )
    logger.info(f"   Avg GP coverage: {gp['coverage_pct'].mean():.1f}%")
    logger.info("=== Silver Layer Complete ✅ ===")
