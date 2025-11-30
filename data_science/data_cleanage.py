import os
import pandas as pd

print("Current working directory:", os.getcwd())

# Set your target directory here
csv_dir = "/home/p89n90/mtg-python-engine/results"
output_file = "merged.csv"

# Collect all CSV files
csv_files = [f for f in os.listdir(csv_dir) if f.endswith(".csv")]

# Store all DataFrames
dfs = []

for file in csv_files:
    full_path = os.path.join(csv_dir, file)
    
    try:
        df = pd.read_csv(full_path)

        # Skip files with no rows (empty or only header)
        if df.empty:
            print(f"Skipped empty or header-only file: {file}")
            continue

        # Add filename for traceability
        df['__source_file'] = file
        dfs.append(df)

    except pd.errors.EmptyDataError:
        print(f"Skipped completely empty file: {file}")
    except Exception as e:
        print(f"Error reading file {file}: {e}")

# Check if we actually have data
if not dfs:
    print("No usable CSV data found. Nothing to merge.")
    exit()

# Concatenate all, allowing for missing columns
merged_df = pd.concat(dfs, ignore_index=True, sort=True)

# Save merged CSV
output_path = os.path.join(csv_dir, output_file)
merged_df.to_csv(output_path, index=False)

print(f"✅ Merged {len(dfs)} CSV files into: {output_path}")
