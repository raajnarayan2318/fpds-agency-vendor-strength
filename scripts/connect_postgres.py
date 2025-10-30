import pandas as pd
from sqlalchemy import create_engine

# --- connection details ---
username = "postgres"         # your PostgreSQL username
password = "your_password"    # your PostgreSQL password
host = "localhost"            # database host
port = "5432"                 # default PostgreSQL port
database = "fpds_project"     # your database name

# --- create connection string ---
connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"

# --- create engine ---
engine = create_engine(connection_string)

# --- test connection and query data ---
query = "SELECT * FROM fpds.actions_clean LIMIT 5;"
df = pd.read_sql(query, engine)

print("✅ Connection successful! Showing first 5 rows:")
# print(df.head())
# print(df[['contracting_agency', 'action_obligation']])

# print(df)
print(df.describe())