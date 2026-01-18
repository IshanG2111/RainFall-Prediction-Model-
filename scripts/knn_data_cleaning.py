import pandas as pd
import numpy as np
from sklearn.neighbors import LocalOutlierFactor
from pathlib import Path

print("\n" + "="*75)
print("KNN DATA CLEANING - RAINFALL PREDICTION PROJECT")
print("="*75)

# PATHS (CORRECTED FOR YOUR FOLDER STRUCTURE)
print("\n[STEP 1/5: CONFIGURING PATHS]")
script_dir = Path(__file__).parent
project_root = script_dir.parent

data_path = project_root / "data_processed" / "8_days"
input_file = data_path / "final_dataset.parquet"
if not input_file.exists():
    input_file = data_path / "final_dataset_8days.parquet"

output_file = data_path / "final_dataset_knn_cleaned.parquet"

print(f"✓ Input:  {input_file}")
print(f"✓ Output: {output_file}")

# LOAD DATA
print("\n[STEP 2/5: LOADING DATA]")
if not input_file.exists():
    print(f"❌ ERROR: File not found!")
    print(f"   Expected: {input_file}")
    print(f"\n   Files in {data_path}:")
    try:
        for f in data_path.glob("*.parquet"):
            print(f"   • {f.name}")
    except:
        pass
    exit(1)

df = pd.read_parquet(input_file)
orig_len = len(df)
num_cols = df.shape  # Get number of columns

# FIXED: Correct formatting
print(f"✓ Loaded: {orig_len:,} rows × {num_cols} columns")

# HANDLE MISSING VALUES
print("\n[STEP 3/5: HANDLING MISSING VALUES]")
missing = df.isnull().sum().sum()
print(f"✓ Missing values: {missing:,}")

if missing > 0:
    df = df.dropna()
    print(f"✓ Dropped rows with missing values: {orig_len - len(df):,}")

# KNN OUTLIER DETECTION
print("\n[STEP 4/5: KNN OUTLIER DETECTION (LOF)]")
print("Processing... (1-2 minutes)")

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
X = df[numeric_cols].values

lof = LocalOutlierFactor(n_neighbors=5, contamination=0.05)
outlier_labels = lof.fit_predict(X)

outliers = (outlier_labels == -1).sum()
inliers = (outlier_labels == 1).sum()

print(f"✓ Outliers detected: {outliers:,} ({outliers/len(df)*100:.2f}%)")
print(f"✓ Clean data: {inliers:,} ({inliers/len(df)*100:.2f}%)")

# REMOVE OUTLIERS & SAVE
print("\n[STEP 5/5: REMOVING OUTLIERS & SAVING]")

df_clean = df[outlier_labels == 1]
df_clean.to_parquet(output_file, compression='snappy', index=False)

rows_removed = orig_len - len(df_clean)
file_size = output_file.stat().st_size / (1024**2)

print(f"✓ Saved: {output_file}")
print(f"✓ File size: {file_size:.2f} MB")

# SUMMARY
print("\n" + "="*75)
print("✅ KNN DATA CLEANING COMPLETE!")
print("="*75)

print(f"""
SUMMARY:
  • Original records: {orig_len:,}
  • Cleaned records: {len(df_clean):,}
  • Outliers removed: {rows_removed:,} ({rows_removed/orig_len*100:.2f}%)
  • Retention rate: {len(df_clean)/orig_len*100:.2f}%
  • Status: ✓ Ready for ML training
  
OUTPUT: {output_file}
""")