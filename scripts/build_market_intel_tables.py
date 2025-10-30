import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# ----- DB -----
USERNAME = "raajthipparthy"
PASSWORD = "root"
HOST = "localhost"
PORT = "5432"
DATABASE = "fpds_project"
ENGINE = create_engine(f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

# We’ll read from your two existing tables:
#   fpds.agency_contractor_scores   (vendor-level features + score)
#   fpds.agency_contractor_tiers    (same rows with tier labels)
scores = pd.read_sql("SELECT * FROM fpds.agency_contractor_scores;", ENGINE)
tiers  = pd.read_sql("SELECT * FROM fpds.agency_contractor_tiers;", ENGINE)

# ---------- 1) Agency Market Size (12m) ----------
agency_market_12m = (
    scores.groupby("contracting_agency", as_index=False)["recent_dollars_12m"]
          .sum()
          .rename(columns={"recent_dollars_12m": "agency_recent_dollars_12m"})
)
# Agency share of total (optional, handy for visuals)
total_all = agency_market_12m["agency_recent_dollars_12m"].sum()
agency_market_12m["agency_share_of_total"] = (
    agency_market_12m["agency_recent_dollars_12m"] / total_all
)
agency_market_12m.to_sql("agency_market_12m", ENGINE, schema="fpds", if_exists="replace", index=False)

# ---------- 2) Vendor Market Share (12m) & HHI ----------
# per agency: vendor 12m and share
vendor_12m = scores[["contracting_agency","vendor_key","legal_business_name","recent_dollars_12m"]].copy()
vendor_12m = vendor_12m[vendor_12m["recent_dollars_12m"].notna()]
vendor_12m = vendor_12m.merge(agency_market_12m, on="contracting_agency", how="left")
vendor_12m["vendor_share_12m"] = (
    vendor_12m["recent_dollars_12m"] / vendor_12m["agency_recent_dollars_12m"].replace(0, np.nan)
)

# HHI per agency: sum of squared shares (×10000 optional for DOJ-style scale)
hhi = (vendor_12m.assign(share_sq=lambda d: d["vendor_share_12m"].fillna(0)**2)
                 .groupby("contracting_agency", as_index=False)["share_sq"].sum())
hhi["hhi_0_1"] = hhi["share_sq"]
hhi["hhi_0_10000"] = (hhi["share_sq"] * 10000).round(0)
hhi = hhi.drop(columns=["share_sq"])

vendor_share_12m = vendor_12m[[
    "contracting_agency","vendor_key","legal_business_name","recent_dollars_12m",
    "agency_recent_dollars_12m","vendor_share_12m"
]].copy()

vendor_share_12m.to_sql("vendor_share_12m", ENGINE, schema="fpds", if_exists="replace", index=False)
hhi.to_sql("agency_hhi", ENGINE, schema="fpds", if_exists="replace", index=False)

# Top 10 vendors per agency (by recent dollars)
top10 = (vendor_12m.sort_values(["contracting_agency","recent_dollars_12m"], ascending=[True,False])
                  .groupby("contracting_agency", as_index=False).head(10)
                  .reset_index(drop=True))
top10.to_sql("top10_vendors_by_agency", ENGINE, schema="fpds", if_exists="replace", index=False)

# ---------- 3) Opportunity Lists ----------
# Merge tiers for tier_label, rank columns for rules
full = scores.merge(tiers[["vendor_key","contracting_agency","tier_label"]], 
                    on=["vendor_key","contracting_agency"], how="left")
full = full.merge(vendor_share_12m[["contracting_agency","vendor_key","vendor_share_12m"]],
                  on=["contracting_agency","vendor_key"], how="left")
full = full.merge(hhi[["contracting_agency","hhi_0_10000"]], on="contracting_agency", how="left")

# Re-engage: Dormant & (Tenure >= 1y or rank_dollars in top quartile within agency)
def add_quartile_flags(df):
    # quartile on rank_dollars per agency
    df["is_top_quartile_dollars"] = df.groupby("contracting_agency")["rank_dollars"]\
                                      .transform(lambda s: s >= s.quantile(0.75))
    return df
full = add_quartile_flags(full)

reengage = full[
    (full["tier_label"] == "Dormant") &
    (
        (full["tenure_years"] >= 1.0) |
        (full["is_top_quartile_dollars"])
    )
].copy()

# Emerging: Tier=Emerging & (Touches >= 2 or rank_touches >= 0.6)
emerging = full[
    (full["tier_label"] == "Emerging") &
    (
        (full["touches_12m"] >= 2) |
        (full["rank_touches"] >= 0.6)
    )
].copy()

# Greenfield: Low concentration agencies + low score + small share
# DOJ guidance: <1500 unconcentrated; treat <=1500 as "low" here.
greenfield = full[
    (full["hhi_0_10000"] <= 1500) &
    (full["relationship_score"] < 40) &
    (full["vendor_share_12m"].fillna(0) < 0.05)
].copy()

# Write lists
reengage.to_sql("oppty_reengage_targets", ENGINE, schema="fpds", if_exists="replace", index=False)
emerging.to_sql("oppty_emerging_targets", ENGINE, schema="fpds", if_exists="replace", index=False)
greenfield.to_sql("oppty_greenfield_targets", ENGINE, schema="fpds", if_exists="replace", index=False)

print("✅ Created tables in schema fpds:")
print(" • agency_market_12m")
print(" • vendor_share_12m")
print(" • agency_hhi")
print(" • top10_vendors_by_agency")
print(" • oppty_reengage_targets")
print(" • oppty_emerging_targets")
print(" • oppty_greenfield_targets")