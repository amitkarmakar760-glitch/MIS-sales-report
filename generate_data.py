"""
SAMPLE - simulated data
Project 04: MIS Sales Report Sample (fictional life insurance branch, Malda area)

All names, policies and numbers are randomly generated. Nothing here is real
company data. Run:  python generate_data.py
Output: 5 CSV files inside the 'data' folder.
"""
import numpy as np
import pandas as pd
from pathlib import Path

# ------------------------------------------------------------
# 1. SETTINGS - change numbers here only
# ------------------------------------------------------------
SEED = 27                       # same seed = same data every run
START = "2022-04-01"            # FY 2022-23 starts
MONTHS = 24                     # Apr 2022 - Mar 2024
OUT_DIR = Path("data")

AREAS = {                       # region: number of staff in that region
    "Malda": 5, "Gazole": 4, "Chanchal": 4,
    "Harischandrapur": 3, "Pakua": 2, "Nalagola": 2,
}
# Fictional names (made up, any match with a real person is a coincidence).
# They are assigned in order of agent_id and use no random numbers, so all other data stays the same.
NAMES = ["Subrata Das", "Anjali Mondal", "Rakesh Sarkar", "Pritha Ghosh", "Sandip Mahato",
         "Rupali Biswas", "Debashis Roy", "Moumita Saha", "Tapan Paul", "Sumana Barman",
         "Biplab Chowdhury", "Kakoli Dutta", "Arindam Hazra", "Shreya Karmakar", "Joydeep Pramanik",
         "Mitali Haldar", "Gautam Sinha", "Nandini Majumder", "Prasenjit Kundu", "Rina Bhowmik"]
N_AGENTS_ONLY = 5               # staff_type 'Agent'; the rest are 'Sales Executive'
CHANNELS = ["Agency", "Bancassurance"]
CHANNEL_PREMIUM_FACTOR = {"Agency": 0.95, "Bancassurance": 1.15}

# product name, product type, share of sales, typical annual premium (Rs)
PRODUCTS = [
    ("Term Plan",      "Term",      0.30, 15000),
    ("Endowment Plan", "Endowment", 0.25, 40000),
    ("ULIP Plan",      "ULIP",      0.20, 50000),
    ("Pension Plan",   "Pension",   0.10, 60000),
    ("Child Plan",     "Child",     0.15, 30000),
]

# month number -> sales multiplier (our assumption: March = financial year end peak)
SEASON = {1: 1.00, 2: 1.05, 3: 1.20, 4: 0.85, 5: 0.90, 6: 0.90,
          7: 0.90, 8: 0.95, 9: 1.00, 10: 1.05, 11: 1.10, 12: 1.00}
GROWTH_FY2 = 1.03               # second financial year sells 5% more
BASE_POLICIES = 4.5             # avg policies per staff per month (before season/skill)
P_INACTIVE = 0.05               # chance a staff member sells nothing in a month
BASE_TARGET = {"Agent": 175000, "Sales Executive": 160000}   # monthly target in Rs

rng = np.random.default_rng(SEED)
OUT_DIR.mkdir(exist_ok=True)

# ------------------------------------------------------------
# 2. STAFF TABLE
# ------------------------------------------------------------
rows, n = [], 1
for region, count in AREAS.items():
    for _ in range(count):
        rows.append({"agent_id": f"A{n:03d}", "agent_name": NAMES[n-1], "region": region})
        n += 1
agents = pd.DataFrame(rows)

agents["staff_type"] = "Sales Executive"
agent_idx = rng.choice(len(agents), N_AGENTS_ONLY, replace=False)
agents.loc[agent_idx, "staff_type"] = "Agent"

# Agents sell through Agency; Sales Executives are mostly Bancassurance
agents["primary_channel"] = np.where(
    agents["staff_type"] == "Agent", "Agency",
    rng.choice(CHANNELS, size=len(agents), p=[0.4, 0.6]))

agents["join_date"] = (pd.to_datetime("2019-01-01")
                       + pd.to_timedelta(rng.integers(0, 1185, len(agents)), unit="D")).date

# hidden skill level: not saved in the file, only drives how much each person sells
skill = dict(zip(agents["agent_id"], rng.normal(1.0, 0.2, len(agents)).clip(0.5, 1.6)))

# ------------------------------------------------------------
# 3. PRODUCT TABLE
# ------------------------------------------------------------
products = pd.DataFrame({
    "product_id": [f"P{i+1:02d}" for i in range(len(PRODUCTS))],
    "product_name": [p[0] for p in PRODUCTS],
    "product_type": [p[1] for p in PRODUCTS],
})
mix = np.array([p[2] for p in PRODUCTS])
typical_premium = np.array([p[3] for p in PRODUCTS])

# ------------------------------------------------------------
# 4. SALES + TARGET TABLES (one loop over staff and months)
# ------------------------------------------------------------
month_starts = pd.date_range(START, periods=MONTHS, freq="MS")
fy2_start = pd.Timestamp("2023-04-01")

sales_parts, target_rows = [], []
for _, a in agents.iterrows():
    for m in month_starts:
        growth = GROWTH_FY2 if m >= fy2_start else 1.0

        # target is set in advance: base x season x growth (no luck involved)
        target = round(BASE_TARGET[a["staff_type"]] * SEASON[m.month] * growth, -3)
        target_rows.append({"agent_id": a["agent_id"], "month": m.date(), "target_premium": target})

        if rng.random() < P_INACTIVE:          # inactive month: no sales
            continue

        n_pol = rng.poisson(BASE_POLICIES * SEASON[m.month] * growth * skill[a["agent_id"]])
        if n_pol == 0:
            continue

        p_idx = rng.choice(len(PRODUCTS), size=n_pol, p=mix)
        premium = (typical_premium[p_idx] * CHANNEL_PREMIUM_FACTOR[a["primary_channel"]]
                   * rng.lognormal(0, 0.2, n_pol))
        sales_parts.append(pd.DataFrame({
            "issue_date": m + pd.to_timedelta(rng.integers(0, m.days_in_month, n_pol), unit="D"),
            "agent_id": a["agent_id"],
            "product_id": products["product_id"].values[p_idx],
            "channel": a["primary_channel"],
            "business_type": rng.choice(["New", "Renewal"], size=n_pol, p=[0.6, 0.4]),
            "premium": np.round(premium, -2),
        }))

sales = pd.concat(sales_parts, ignore_index=True).sort_values("issue_date").reset_index(drop=True)
sales.insert(0, "policy_id", [f"SMP{i+1:06d}" for i in range(len(sales))])
sales["issue_date"] = sales["issue_date"].dt.date
target = pd.DataFrame(target_rows)

# ------------------------------------------------------------
# 5. CLAIMS TABLE (separate department data, small table)
# ------------------------------------------------------------
region_p = np.array(list(AREAS.values())) / sum(AREAS.values())
claim_mix = np.array([0.35, 0.30, 0.15, 0.05, 0.15])
cutoff = pd.Timestamp("2024-01-31")             # claims received after this may still be pending

claim_parts = []
for m in month_starts:
    k = rng.poisson(8)
    received = m + pd.to_timedelta(rng.integers(0, m.days_in_month, k), unit="D")
    status = [
        rng.choice(["Settled", "Pending", "Rejected"], p=[0.55, 0.40, 0.05]) if d > cutoff
        else rng.choice(["Settled", "Rejected"], p=[0.94, 0.06])
        for d in received
    ]
    claim_parts.append(pd.DataFrame({
        "received_date": received,
        "region": rng.choice(list(AREAS.keys()), size=k, p=region_p),
        "product_id": products["product_id"].values[rng.choice(len(PRODUCTS), size=k, p=claim_mix)],
        "status": status,
        "claim_amount": np.round(rng.lognormal(np.log(300000), 0.8, k), -3),
    }))
claims = pd.concat(claim_parts, ignore_index=True).sort_values("received_date").reset_index(drop=True)
claims.insert(0, "claim_id", [f"CLM{i+1:05d}" for i in range(len(claims))])
claims["received_date"] = claims["received_date"].dt.date

# ------------------------------------------------------------
# 6. SAVE (file names start with SAMPLE_ so nobody mistakes it for real data)
# ------------------------------------------------------------
agents.to_csv(OUT_DIR / "SAMPLE_dim_agent.csv", index=False)
products.to_csv(OUT_DIR / "SAMPLE_dim_product.csv", index=False)
sales.to_csv(OUT_DIR / "SAMPLE_fact_sales.csv", index=False)
target.to_csv(OUT_DIR / "SAMPLE_fact_target.csv", index=False)
claims.to_csv(OUT_DIR / "SAMPLE_fact_claims.csv", index=False)

# ------------------------------------------------------------
# 7. QUICK CHECKS (print only)
# ------------------------------------------------------------
print("SAMPLE - simulated data")
print("Rows -> staff:", len(agents), "| products:", len(products), "| sales:", len(sales),
      "| targets:", len(target), "| claims:", len(claims))

s = sales.copy()
s["month"] = pd.to_datetime(s["issue_date"]).dt.to_period("M")
t = target.copy()
t["month"] = pd.to_datetime(t["month"]).dt.to_period("M")
monthly = pd.DataFrame({"premium": s.groupby("month")["premium"].sum(),
                        "target": t.groupby("month")["target_premium"].sum()})
monthly["ach_%"] = (monthly["premium"] / monthly["target"] * 100).round(1)
print(monthly)
print("Overall achievement %:", round(monthly["premium"].sum() / monthly["target"].sum() * 100, 1))
