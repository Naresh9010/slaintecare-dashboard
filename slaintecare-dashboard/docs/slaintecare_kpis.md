# Sláintecare KPI Definitions & Targets

## What is Sláintecare?

Sláintecare is Ireland's 10-year health reform programme (2018–2028), approved unanimously by the Oireachtas. It aims to build a universal, single-tier health system where access is based on need, not ability to pay.

Key pillars:
1. Reduce waiting lists to maximum 12 weeks (OP) and 10 weeks (IPDC)
2. Universal GP care without fees
3. Shift care from hospitals to communities
4. Establish 6 Regional Health Areas (RHAs)

---

## KPIs Tracked in This Dashboard

### Waiting List KPIs (NTPF Data)

| KPI | Definition | Sláintecare Target |
|---|---|---|
| Total OP Waiting | Total patients waiting for first outpatient appointment | Reduce year-on-year |
| % Beyond 12-Week Target | % of OP patients waiting more than 12 weeks | 0% |
| % Waiting Over 12 Months | % of patients waiting more than 52 weeks | 0% |
| Total IPDC Waiting | Total patients waiting for inpatient/day case procedure | Reduce year-on-year |
| % Beyond 10-Week IPDC Target | % of IPDC patients waiting more than 10 weeks | 0% |

### ED / Emergency KPIs (HSE TrolleyGAR)

| KPI | Definition | Sláintecare Target |
|---|---|---|
| Average Daily Trolleys | Patients awaiting admission on trolleys/chairs in ED | 50% reduction by 2027 |
| Hospital Breach Count | Hospitals exceeding daily trolley threshold | 0 |

### Primary Care KPIs (HSE Eligibility Data)

| KPI | Definition | Sláintecare Target |
|---|---|---|
| GP Visit Card Coverage | % of population with GP Visit Card eligibility | 100% (universal) |
| Medical Card Coverage | % of population with Medical Card | >40% |

---

## Wait Time Bands (NTPF Schema)

| Band | Description | Sláintecare Status |
|---|---|---|
| 0–6 Weeks | Within target | ✅ On Target |
| 6–12 Weeks | Within target | ✅ On Target |
| 12–18 Weeks | Beyond OP target | ⚠️ Breach |
| 18–24 Weeks | Significantly beyond target | 🔶 Serious |
| 24–36 Weeks | Very long wait | 🔶 Serious |
| 36–52 Weeks | Critical | 🔴 Critical |
| 52+ Weeks | Over 12 months — Sláintecare zero tolerance | 🔴 Critical |

---

## Regional Health Areas (RHAs)

Sláintecare restructured the HSE into 6 Regional Health Areas replacing the previous CHO structure:

| RHA | Counties / Area |
|---|---|
| Dublin & North East | Dublin North, Meath, Louth, Cavan, Monaghan |
| Dublin & Midlands | Dublin South, Kildare, Wicklow, Laois, Offaly, Longford, Westmeath |
| South West | Cork, Kerry |
| South East | Wexford, Waterford, Kilkenny, Carlow, South Tipperary |
| West | Galway, Mayo, Roscommon |
| Mid West | Limerick, Clare, North Tipperary |

---

## References

- Sláintecare Implementation Strategy: https://www.gov.ie/en/publication/slaintecare
- NTPF Waiting List Reports: https://www.ntpf.ie/waiting-list-data
- HSE Performance Reports: https://www.hse.ie/eng/services/publications/performancereports
