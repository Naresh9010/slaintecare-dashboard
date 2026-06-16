# Data Sources

All data used in this project is **free, public, and openly licensed** under the Open Government Licence (Ireland).

---

## 1. NTPF — National Treatment Purchase Fund

**Website:** https://www.ntpf.ie/waiting-list-data/open-data/

| Dataset | Description | Direct Download |
|---|---|---|
| OP Waiting List by Hospital 2026 | Outpatient waiting list by hospital, monthly | [Download](https://www.ntpf.ie/home/OpenData/OP%20Waiting%20List%20By%20Hospital%202026.csv) |
| OP Waiting List by Hospital 2025 | Outpatient waiting list by hospital, monthly | [Download](https://www.ntpf.ie/home/OpenData/OP%20Waiting%20List%20By%20Hospital%202025.csv) |
| IPDC Waiting List by Hospital 2026 | Inpatient/Day Case by hospital | [Download](https://www.ntpf.ie/home/OpenData/IPDC%20Waiting%20List%20By%20Hospital%202026.csv) |
| GI Endoscopy by Hospital 2026 | Endoscopy waiting list | [Download](https://www.ntpf.ie/home/OpenData/GI%20Endoscopy%20Waiting%20List%20By%20Hospital%202026.csv) |

**Update frequency:** Monthly (second Friday of each month)

---

## 2. HSE Open Data Portal

**Website:** https://data.ehealthireland.ie

| Dataset | Description |
|---|---|
| GP Visit Card Eligibility | Number of persons with GP Visit Cards by CHO, gender, and age group |
| Medical Card Eligibility | Number of persons with Medical Cards by CHO |
| eReferral Activity | GP to hospital referral volumes |

---

## 3. data.gov.ie — Ireland's National Open Data Portal

**Website:** https://data.gov.ie

| Dataset | Description |
|---|---|
| CSO Population by County | Census 2022 population estimates |
| HSE Bed Capacity | Hospital bed numbers by hospital |

---

## How to Download Real Data

```python
# Run the NTPF loader to automatically download all available years
python src/ingestion/ntpf_loader.py

# This will download to: data/raw/ntpf/
# Files are named: op_by_hospital_2025.csv, ipdc_by_hospital_2025.csv etc.
```

---

## Licence

All datasets are published under the **Open Government Licence — Ireland**
https://data.gov.ie/pages/licence
