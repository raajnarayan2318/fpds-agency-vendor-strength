# FPDS Agency–Contractor Relationship Strength

An end-to-end analytics project using PostgreSQL + Python:
- Clean FPDS data into SQL
- Compute relationship scores + tiers (Elite/Core/Emerging/Prospect/Dormant)
- Build market-intel tables (HHI, vendor share, top vendors)
- Visualize results with Python

## How to run
1) Install Python deps: `pip install -r requirements.txt`
2) Configure DB creds in `scripts/*.py`
3) Run scripts in `scripts/` in order (scores → tiers → market intel → visuals)

## Repo structure
- `scripts/` – Python ETL/analytics/visuals
- `outputs/` – charts
- `docs/` – report & optional schema notes
- `data/` – datasets (store only what you want public)

## Notes
- This repo excludes large raw data and local secrets by default.
