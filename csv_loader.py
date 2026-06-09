import pandas as pd
import sqlite3

csv_path = r"C:\Users\polen\Downloads\Spreadsheets\Electric_Vehicle_Population_Data.csv"

# Read CSV
df = pd.read_csv(csv_path)

# Write to database
conn = sqlite3.connect('electric_vehicles.db')
df.to_sql('vehicles', conn, if_exists='replace', index=False)
print("Loaded into database successfully.")

# Query it back
# Top 10 most common Make and Model combinations
result = pd.read_sql("SELECT Make, Model, COUNT(*) as total FROM vehicles GROUP BY Make, Model ORDER BY total DESC LIMIT 10", conn)
# Top 10 states with the most electric vehicles
state_result = pd.read_sql("SELECT State, COUNT(*) as total FROM vehicles GROUP BY State ORDER BY total DESC LIMIT 10", conn)
# Average range by Make
range_result = pd.read_sql("SELECT Make, AVG(\"Electric Range\") as avg_range FROM vehicles GROUP BY Make ORDER BY avg_range DESC LIMIT 10", conn)
# How Many EVs were registered per Model Year
model_year_result = pd.read_sql('SELECT "Model Year", COUNT(*) as total FROM vehicles GROUP BY "Model Year" ORDER BY "Model Year" DESC', conn)
print(result)
print(state_result)
print(range_result)
print(model_year_result)

conn.close()