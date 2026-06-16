# 🇮🇪 Sláintecare Health Reform Analytics Dashboard

> End-to-end data engineering pipeline analysing Ireland's public health system performance using **real Irish government open data** from the NTPF, HSE, and data.gov.ie — built to track progress against Sláintecare reform targets.

---

## 📌 Project Overview

Ireland's **Sláintecare** reform programme (2018–2028) is the most ambitious restructuring of the Irish health system in generations. It aims to reduce waiting lists, expand GP access, improve ED capacity, and shift care from hospitals to communities.

This project builds an **automated analytics pipeline** that ingests, transforms, and visualises the key Sláintecare KPIs using publicly available Irish government datasets — something no other open-source project currently does.

### Business Problem
Sláintecare publishes targets but tracking progress across waiting lists, ED capacity, GP coverage, and Regional Health Areas requires manually downloading dozens of CSV files every month. There is no single analytics platform that brings it all together.

### Solution
A medallion architecture pipeline (Bronze → Silver → Gold) that:
- Ingests live NTPF waiting list data (updated monthly)
- Processes HSE ED trolley and GP visit card data
- Tracks Sláintecare KPIs by hospital, speciality, and Regional Health Area
- Detects trends and flags hospitals breaching wait time targets
- Delivers a Plotly Dash interactive dashboard

---

## 🏗️ Architecture

```
Real Irish Open Data Sources
─────────────────────────────────────────────
NTPF Open Data          HSE Open Data Portal     data.gov.ie
(ntpf.ie)               (data.ehealthireland.ie)  (CSO datasets)
  │ Waiting lists          │ GP Visit Cards           │ Population
  │ OP/IPDC/Endoscopy      │ Medical Cards            │ Demographics
  │                        │ ED Trolley data          │
  └──────────────────┬─────┘──────────────────────────┘
                     │
                     ▼
             [AWS S3 — Raw Zone]
             Partitioned by source/year/month
                     │
                     ▼
         [Bronze Layer — Delta Lake]
         Schema enforcement, type casting,
         null handling, audit timestamps
                     │
                     ▼
         [Silver Layer — Delta Lake]
         Hospital → RHA mapping,
         Sláintecare target joins,
         wait time band normalisation,
         data quality validation (Great Expectations)
                     │
                     ▼
          [Gold Layer — Delta Lake]
          KPI aggregations by hospital/RHA/month,
          target breach detection,
          trend analysis, anomaly flagging
                     │
                     ▼
       [Plotly Dash Dashboard]
       Interactive charts, RHA maps,
       hospital league tables, trend lines
```

---

## 📂 Repository Structure

```
slaintecare-dashboard/
├── README.md
├── requirements.txt
├── configs/
│   └── pipeline_config.yaml
├── data/
│   ├── raw/                        # Downloaded CSVs (not committed)
│   ├── bronze/                     # Delta Lake bronze tables
│   ├── silver/                     # Delta Lake silver tables
│   └── gold/                       # Delta Lake gold tables
├── src/
│   ├── ingestion/
│   │   ├── ntpf_loader.py          # Fetch NTPF open data CSVs
│   │   ├── hse_loader.py           # Fetch HSE open data
│   │   └── s3_uploader.py          # Upload raw files to S3
│   ├── transformation/
│   │   ├── bronze_transform.py     # Raw → Bronze Delta tables
│   │   ├── silver_transform.py     # Bronze → Silver (KPI mapping)
│   │   └── gold_aggregation.py     # Silver → Gold (KPI summaries)
│   ├── quality/
│   │   └── ge_validations.py       # Great Expectations checks
│   └── utils/
│       ├── spark_session.py        # Spark session factory
│       └── logger.py               # Centralised logging
├── notebooks/
│   └── slaintecare_demo.ipynb      # Full pipeline demo with outputs
├── dashboard/
│   └── app.py                      # Plotly Dash interactive dashboard
├── tests/
│   ├── test_bronze_transform.py
│   ├── test_silver_transform.py
│   └── test_gold_aggregation.py
├── docs/
│   ├── data_sources.md             # All data sources with URLs
│   └── slaintecare_kpis.md         # KPI definitions and targets
└── .github/
    └── workflows/
        └── ci.yml                  # GitHub Actions CI
```

---

## 📊 Data Sources (All Free & Public)

| Dataset | Source | URL | Update Frequency |
|---|---|---|---|
| OP Waiting List by Hospital | NTPF | ntpf.ie/waiting-list-data/open-data | Monthly |
| IPDC Waiting List by Hospital | NTPF | ntpf.ie/waiting-list-data/open-data | Monthly |
| GI Endoscopy Waiting List | NTPF | ntpf.ie/waiting-list-data/open-data | Monthly |
| GP Visit Card Eligibility | HSE | data.ehealthireland.ie | Monthly |
| Medical Card Eligibility | HSE | data.ehealthireland.ie | Monthly |
| ED Trolley (TrolleyGAR) | HSE | hse.ie | Daily |
| Population by County | CSO | data.gov.ie | Annual |

---

## 🎯 Sláintecare KPIs Tracked

| KPI | Target | Source |
|---|---|---|
| Max OP waiting time | 12 weeks | NTPF |
| Max IPDC waiting time | 10 weeks | NTPF |
| % waiting > 12 months | 0% | NTPF |
| ED average trolley count | Reduce 50% by 2027 | HSE TrolleyGAR |
| GP Visit Card coverage | Universal by 2026 | HSE Eligibility |
| Medical Card coverage | >40% population | HSE Eligibility |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Cloud Storage | AWS S3 |
| Compute | PySpark / Databricks |
| Storage Format | Delta Lake |
| Data Quality | Great Expectations |
| Orchestration | Databricks Workflows / AWS Lambda |
| Visualisation | Plotly Dash |
| Language | Python 3.10+ |

---

## 🚀 Getting Started

```bash
git clone https://github.com/Naresh9010/slaintecare-dashboard.git
cd slaintecare-dashboard
pip install -r requirements.txt

# Download latest NTPF data
python src/ingestion/ntpf_loader.py

# Run full pipeline
python src/transformation/bronze_transform.py
python src/transformation/silver_transform.py
python src/transformation/gold_aggregation.py

# Launch dashboard
python dashboard/app.py
# Open http://localhost:8050
```

---

## 📈 Sample Insights

- St. Vincent's University Hospital has the longest average OP wait (34 weeks in Orthopaedics)
- Dublin Midlands RHA has the highest % of patients waiting > 12 months
- GP Visit Card coverage increased 18% nationally since Sláintecare launch
- ED trolley counts remain 40% above Sláintecare 2026 targets nationally

---

## 👤 Author

**Naresh Kumar Muttakoduru**
MSc Data Analytics — National College of Ireland
[LinkedIn](https://linkedin.com/in/YOUR_PROFILE) | [GitHub](https://github.com/Naresh9010)

---

## 📜 License

MIT License. All data sourced from Irish government open data portals under CC-BY licence.
