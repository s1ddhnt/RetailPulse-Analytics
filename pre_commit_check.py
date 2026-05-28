"""
RetailPulse Pre-Commit Data Validation
Run this before every GitHub commit to verify both CSVs are clean.
Usage: python pre_commit_check.py
"""

import pandas as pd
import sys

PASS = "✅"
FAIL = "❌"
issues = []

def check(label, condition, detail=""):
    status = PASS if condition else FAIL
    print(f"  {status}  {label}" + (f"  →  {detail}" if detail else ""))
    if not condition:
        issues.append(label)

# ─────────────────────────────────────────────
print("\n══════════════════════════════════════════")
print("  retailpulse_clean.csv")
print("══════════════════════════════════════════")

df = pd.read_csv("data/retailpulse_clean.csv")

check("Row count ≥ 1,000,000",       len(df) >= 999_000,           f"{len(df):,} rows")
check("Exactly 16 columns",          df.shape[1] == 16,              f"{df.shape[1]} columns")
check("No missing values",           df.isnull().sum().sum() == 0,   f"{df.isnull().sum().sum()} nulls")
check("No duplicate rows",           df.duplicated().sum() == 0,     f"{df.duplicated().sum()} dupes")
check("No negative Quantity",        (df['Quantity'] < 0).sum() == 0)
check("No negative UnitPrice",       (df['UnitPrice'] <= 0).sum() == 0)
check("No negative TotalPrice",      (df['TotalPrice'] < 0).sum() == 0)
check("Quantity capped at 144",      df['Quantity'].max() <= 144,    f"max={df['Quantity'].max()}")
check("UnitPrice capped at 12.75",   df['UnitPrice'].max() <= 12.75, f"max={df['UnitPrice'].max()}")
check("No junk descriptions",        ~df['Description'].str.upper().isin(
                                     ['MANUAL','POSTAGE','DOTCOM POSTAGE',
                                      'BANK CHARGES','DISCOUNT']).any())
check("Year range 2009–2012",        df['Year'].between(2009, 2012).all(),
                                     f"{df['Year'].min()}–{df['Year'].max()}")
check("Hour range 6–20",             df['Hour'].between(6, 20).all())
check("No Saturday transactions",    (df['DayOfWeek'] == 5).sum() == 0,
                                     f"{(df['DayOfWeek']==5).sum()} Saturday rows")
check("TotalPrice = Qty × Price",    ((df['Quantity'] * df['UnitPrice']).round(2)
                                     - df['TotalPrice'].round(2)).abs().max() < 0.01)
check("CustomerID all integers",     df['CustomerID'].dtype in ['int64','int32'])
check("Unique customers > 5000",     df['CustomerID'].nunique() > 5000,
                                     f"{df['CustomerID'].nunique():,} customers")

# ─────────────────────────────────────────────
print("\n══════════════════════════════════════════")
print("  retailpulse_rfm.csv")
print("══════════════════════════════════════════")

rfm = pd.read_csv("data/retailpulse_rfm.csv")

expected_cols = ['CustomerID','Recency','Frequency','Monetary',
                 'R_Score','F_Score','M_Score','RFM_Score','RFM_Total','Segment']

check("Exactly 10 columns",          rfm.shape[1] == 10,             f"{rfm.shape[1]} columns")
check("All expected columns exist",  all(c in rfm.columns for c in expected_cols))
check("No missing values",           rfm.isnull().sum().sum() == 0,  f"{rfm.isnull().sum().sum()} nulls")
check("No duplicate CustomerIDs",    rfm.duplicated('CustomerID').sum() == 0,
                                     f"{rfm.duplicated('CustomerID').sum()} dupes")
check("Recency ≥ 0",                 (rfm['Recency'] >= 0).all())
check("Frequency ≥ 1",              (rfm['Frequency'] >= 1).all())
check("Monetary > 0",               (rfm['Monetary'] > 0).all())
check("All 6 segments present",      set(['Champions','Loyal Customers','Potential Loyalists',
                                     'At Risk','Lost','New Customers'])
                                     .issubset(set(rfm['Segment'].unique())))
check("RFM scores are 1–5",          rfm[['R_Score','F_Score','M_Score']].isin([1,2,3,4,5]).all().all())

# ─────────────────────────────────────────────
print("\n══════════════════════════════════════════")
if issues:
    print(f"  {FAIL}  {len(issues)} issue(s) found — fix before committing:")
    for i in issues:
        print(f"       → {i}")
else:
    print(f"  {PASS}  All checks passed — safe to commit!")
print("══════════════════════════════════════════\n")

sys.exit(1 if issues else 0)
