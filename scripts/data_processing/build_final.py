import pandas as pd
from scripts.config.phase_config import PHASE_CONFIG
from scripts.final_imputation.load_files import load_master_daily_files
from scripts.final_imputation.temporal_data import add_temporal_metadata
from scripts.final_imputation.apply_imputation import apply_imputation

def run_build_final(phase_name: str):
    if phase_name not in PHASE_CONFIG:
        raise ValueError(f"Phase '{phase_name}' not found in PHASE_CONFIG")

    cfg = PHASE_CONFIG[phase_name]
    processed_base_dir = cfg["processed_base_dir"]

    print(f"\nStarting BUILD FINAL for phase: {phase_name}")

    daily_dfs = load_master_daily_files(processed_base_dir)

    df = pd.concat(daily_dfs, ignore_index=True)
    print(f"Combined dataset shape: {df.shape}")

    df = add_temporal_metadata(df)

    df = apply_imputation(df)

    if "rain_mm" in df.columns:
        before = len(df)
        df = df.dropna(subset=["rain_mm"])
        after = len(df)
        print(f"Dropped {before - after} rows with missing rainfall target")

    final_dir = processed_base_dir / "final_dataset"
    final_dir.mkdir(parents=True, exist_ok=True)

    outpath = final_dir/"final_dataset.parquet"
    df.to_parquet(outpath, index=False)

    print(f"Final dataset saved → {outpath}")
    print(f"Final dataset shape: {df.shape}")


if __name__ == "__main__":
    while True:
        print("\nBUILD FINAL MENU")
        print("1. Build final dataset for 2_days")
        print("2. Build final dataset for 8_days")
        print("3. Build final dataset for 3_months")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ").strip()
        if choice == "1":
            run_build_final("2_days")
        elif choice == "2":
            run_build_final("8_days")
        elif choice == "3":
            run_build_final("3_months")
        elif choice == "4":
            print("Exiting build-final pipeline.")
            break
        else:
            print("Invalid choice. Please try again.")