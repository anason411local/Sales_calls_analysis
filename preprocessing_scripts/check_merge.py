import pandas as pd

df = pd.read_csv('export_lgs_omc_2025_12_16.csv')
print(f'Total rows: {len(df)}')
print(f'Rows with company_name filled: {df["company_name"].notna().sum()}')
print(f'Rows with service filled: {df["service"].notna().sum()}')
print(f'Rows with address filled: {df["address"].notna().sum()}')
print(f'Rows with city filled: {df["city"].notna().sum()}')
print(f'Rows with state filled: {df["state"].notna().sum()}')
print('\nSample of rows with merged data:')
filled = df[df['company_name'].notna()][['lead_id', 'company_name', 'service', 'city', 'state', 'postal_code']].head(10)
print(filled)

