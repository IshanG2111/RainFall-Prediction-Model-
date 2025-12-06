import pandas as pd
import os
import functools

def merge_datasets(data_dir="data_processed"):
    """
    Merges all product CSVs into a single master DataFrame.
    """
    products = ['IMC', 'HEM', 'WDP', 'UTH', 'OLR', 'LST', 'CMP']
    dfs = []
    
    print("Reading product files...")
    for prod in products:
        path = os.path.join(data_dir, f"{prod}_mock.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            dfs.append(df)
            print(f"Loaded {prod}: {df.shape}")
        else:
            print(f"Warning: {path} not found.")
    
    if not dfs:
        print("No data found to merge.")
        return

    print("Merging datasets...")
    # Merge all dataframes on date and grid_id
    master_df = functools.reduce(lambda left, right: pd.merge(left, right, on=['date', 'grid_id'], how='inner'), dfs)
    
    print(f"Merged shape: {master_df.shape}")
    
    # Add some derived time features
    master_df['date'] = pd.to_datetime(master_df['date'])
    master_df['month'] = master_df['date'].dt.month
    master_df['day_of_year'] = master_df['date'].dt.dayofyear
    
    output_path = os.path.join(data_dir, "master_dataset.parquet")
    master_df.to_parquet(output_path, index=False)
    print(f"Saved master dataset to {output_path}")
    
    # Also save a small CSV sample for inspection
    master_df.head(100).to_csv(os.path.join(data_dir, "master_sample.csv"), index=False)

if __name__ == "__main__":
    merge_datasets()
