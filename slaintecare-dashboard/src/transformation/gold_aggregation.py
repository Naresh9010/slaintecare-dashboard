"""
gold_aggregation.py
Silver → Gold layer.
Final KPI aggregations ready for the Plotly Dash dashboard.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger


def build_gold_hospital_kpis(silver_path: str, output_path: str) -> pd.DataFrame:
    """
    Aggregates waiting list KPIs to hospital level — monthly and annual.
    This is the primary Power BI / Dash data source.
    """
    logger.info("Building Gold hospital KPI table...")

    df = pd.read_parquet(silver_path)

    gold = (
        df.groupby(["month_str", "year", "month", "hospital", "rha"])
        .agg(
            total_waiting        = ("total_waiting",        "sum"),
            waiting_beyond_target= ("waiting_beyond_target","sum"),
            waiting_over_12m     = ("w_52_plus",            "sum"),
            avg_pct_beyond_target= ("pct_beyond_target",    "mean"),
            avg_pct_over_12m     = ("pct_over_12_months",   "mean"),
            specialities_tracked = ("speciality",           "nunique"),
            breach_count         = ("target_breached",      "sum"),
        )
        .reset_index()
    )

    gold["avg_pct_beyond_target"] = gold["avg_pct_beyond_target"].round(2)
    gold["avg_pct_over_12m"]      = gold["avg_pct_over_12m"].round(2)

    gold["hospital_status"] = pd.cut(
        gold["avg_pct_beyond_target"],
        bins=[-1, 0, 20, 50, 100],
        labels=["On Target ✅", "Moderate ⚠️", "Serious 🔶", "Critical 🔴"]
    )

    gold["gold_processed_at"] = pd.Timestamp.now()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    gold.to_parquet(output_path, index=False)
    logger.info(f"✅ Gold hospital KPIs: {len(gold):,} rows → {output_path}")
    return gold


def build_gold_rha_summary(silver_path: str, output_path: str) -> pd.DataFrame:
    """
    Aggregates KPIs to Regional Health Area level.
    """
    logger.info("Building Gold RHA summary table...")

    df = pd.read_parquet(silver_path)

    rha = (
        df.groupby(["month_str", "year", "rha"])
        .agg(
            total_waiting         = ("total_waiting",        "sum"),
            waiting_beyond_target = ("waiting_beyond_target","sum"),
            waiting_over_12m      = ("w_52_plus",            "sum"),
            hospitals_tracked     = ("hospital",             "nunique"),
            critical_hospitals    = ("target_breached",      "sum"),
        )
        .reset_index()
    )

    rha["pct_beyond_target"] = (
        rha["waiting_beyond_target"] / rha["total_waiting"] * 100
    ).round(2)

    rha["pct_over_12_months"] = (
        rha["waiting_over_12m"] / rha["total_waiting"] * 100
    ).round(2)

    rha["gold_processed_at"] = pd.Timestamp.now()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    rha.to_parquet(output_path, index=False)
    logger.info(f"✅ Gold RHA summary: {len(rha):,} rows → {output_path}")
    return rha


def build_gold_national_trend(silver_path: str, output_path: str) -> pd.DataFrame:
    """
    Monthly national-level KPI trend — used for headline charts.
    """
    logger.info("Building Gold national trend table...")

    df = pd.read_parquet(silver_path)

    national = (
        df.groupby(["month_str", "year", "month"])
        .agg(
            total_waiting         = ("total_waiting",        "sum"),
            waiting_beyond_target = ("waiting_beyond_target","sum"),
            waiting_over_12m      = ("w_52_plus",            "sum"),
        )
        .reset_index()
        .sort_values(["year", "month"])
    )

    national["pct_beyond_target"] = (
        national["waiting_beyond_target"] / national["total_waiting"] * 100
    ).round(2)

    national["pct_over_12_months"] = (
        national["waiting_over_12m"] / national["total_waiting"] * 100
    ).round(2)

    # Rolling 3-month average for trend line
    national["pct_beyond_target_3m_avg"] = (
        national["pct_beyond_target"].rolling(3, min_periods=1).mean().round(2)
    )

    national["gold_processed_at"] = pd.Timestamp.now()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    national.to_parquet(output_path, index=False)
    logger.info(f"✅ Gold national trend: {len(national):,} rows → {output_path}")
    return national


if __name__ == "__main__":
    logger.info("=== Gold Layer: KPI Aggregations ===")

    hospital_kpis = build_gold_hospital_kpis(
        "data/silver/waiting_list.parquet",
        "data/gold/hospital_kpis.parquet"
    )

    rha_summary = build_gold_rha_summary(
        "data/silver/waiting_list.parquet",
        "data/gold/rha_summary.parquet"
    )

    national_trend = build_gold_national_trend(
        "data/silver/waiting_list.parquet",
        "data/gold/national_trend.parquet"
    )

    logger.info(f"   Hospitals tracked: {hospital_kpis['hospital'].nunique()}")
    logger.info(f"   RHAs tracked: {rha_summary['rha'].nunique()}")
    logger.info(f"   Months tracked: {national_trend['month_str'].nunique()}")
    logger.info("=== Gold Layer Complete ✅ ===")
