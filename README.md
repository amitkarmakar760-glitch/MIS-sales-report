# Project 04: MIS Sales Report Sample

> **SAMPLE - simulated data.** Every number, name and policy here is randomly generated for a fictional life insurance branch (Malda area). It is not real company data and is not the work product of any employer.

## What this project shows
The kind of monthly MIS reporting a branch manager asks for: target vs achievement, product-wise, channel-wise, region-wise and staff-wise performance, new vs renewal business, top and bottom performers, and a claims summary.

## Files
| File | Purpose |
|---|---|
| `generate_data.py` | Generates the fictional dataset (seed 27, reproducible) |
| `data/SAMPLE_*.csv` | The 5 generated tables |
| `Project04_MIS_Sample.xlsx` | Excel workbook: data tables, summary sheets, dashboard with month selector, data checks |
| `Monthly_MIS_Report_Mar2024.pdf` | Monthly MIS report for March 2024 |
| `Management_Summary_FY2324.pdf` | One-page management summary for the annual review |
| `Project04_OnePager.pdf` | One-page project summary |
| `Dashboard_Excel.pdf` / `.png` | Dashboard export and screenshot |

## Dataset (all simulated)
* 20 sales staff (5 Agents, 15 Sales Executives) in 6 areas: Malda, Gazole, Chanchal, Harischandrapur, Pakua, Nalagola
* 2 channels (Agency, Bancassurance), 5 products, 24 months (Apr 2022 - Mar 2024)
* 2,121 policy rows, 480 monthly targets (20 staff x 24 months), 189 claims

| Table | Main columns |
|---|---|
| `SAMPLE_dim_agent` | agent_id, agent_name, region, staff_type, primary_channel, join_date |
| `SAMPLE_dim_product` | product_id, product_name, product_type |
| `SAMPLE_fact_sales` | policy_id, issue_date, agent_id, product_id, channel, business_type (New/Renewal), premium |
| `SAMPLE_fact_target` | agent_id, month, target_premium |
| `SAMPLE_fact_claims` | claim_id, received_date, region, product_id, status (Settled/Rejected/Pending), claim_amount |

## Report questions answered
1. Target vs achievement by month  2. Which staff met target  3. Product-wise premium and share  4. Channel-wise policies and premium  5. Region-wise performance
6. New vs renewal premium  7. Top 5 and bottom 5 staff  8. Month-on-month and year-on-year growth  9. Total vs producing staff  10. Average premium per policy  11. Claim settlement ratio

## How to reproduce
```
python -m pip install pandas numpy
python generate_data.py
```
The script prints a monthly check table. Overall achievement should be 98.2% and total premium Rs 7,76,63,000.

## Key findings (simulated data)
* FY 2023-24 premium Rs 410.17 lakh, +11.9% on FY 2022-23; achievement 102.2% vs 94.0%
* Harischandrapur reached 111.7% of target, Pakua 91.9%
* 5 of 20 staff finished below 80% of their 24-month target; March 2024 closed at 88.4% of target

## Definitions
Achievement % = premium / target. Producing staff = staff with at least one policy in the month. Claim settlement ratio = settled / (settled + rejected), pending excluded. Financial year runs April to March.

## Assumptions and limitations
* Seasonality (March, February and Oct-Nov higher, April low) is an assumption, not calibrated to real data.
* Targets are fixed in advance; premium varies with product, channel, staff skill and random variation.
* Customer age, sum assured and persistency are not modelled. Renewal rows are not linked to an original policy.
* Data is random, so month-to-month swings are noise. Results show method, not real business facts.
* Summary sheets use SUMIFS / COUNTIFS formulas rather than PivotTables.

## Tools
Python (pandas, numpy), Excel, reportlab and matplotlib for the PDFs. A Power BI version of the dashboard is planned.

Author: Amit Karmakar. GitHub / Drive links: add here.
