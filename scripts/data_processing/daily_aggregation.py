from scripts.config.phase_config import PHASE_CONFIG
from scripts.grid.grid_loader import load_grid_definition
from scripts.features.imc_daily import process_imc_daily
from scripts.features.wdp_daily import process_wdp_daily
from scripts.features.lst_daily import process_lst_daily
from scripts.features.cmp_daily import process_cmp_daily
from scripts.features.uth_daily import process_uth_daily
from scripts.features.olr_daily import process_olr_daily
from scripts.features.hem_daily import process_hem_daily

def run_daily_aggregation(phase_name: str):
    if phase_name not in PHASE_CONFIG:
        raise ValueError(f"Phase '{phase_name}' not found in PHASE_CONFIG")

    cfg = PHASE_CONFIG[phase_name]

    dates = cfg["dates"]

    # Load grid once
    grid_df = load_grid_definition()

    print(f"\nStarting DAILY AGGREGATION for phase: {phase_name}")
    print(f"Total days: {len(dates)}")

    for d in dates:
        print(f"Processing date: {d}")

        process_imc_daily(d, cfg, grid_df)
        process_wdp_daily(d, cfg, grid_df)
        process_lst_daily(d, cfg, grid_df)
        process_cmp_daily(d, cfg, grid_df)
        process_uth_daily(d, cfg, grid_df)
        process_olr_daily(d, cfg, grid_df)
        process_hem_daily(d, cfg, grid_df)

    print("\nAll daily aggregation tasks completed successfully!")


if __name__ == "__main__":
    while True:
        print("\nDAILY AGGREGATION MENU")
        print("1. Run 2_days pipeline")
        print("2. Run 8_days pipeline")
        print("3. Run 3_months pipeline")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ").strip()
        if choice == "1":
            run_daily_aggregation("2_days")
        elif choice == "2":
            run_daily_aggregation("8_days")
        elif choice == "3":
            run_daily_aggregation("3_months")
        elif choice == "4":
            print("Exiting pipeline.")
            break
        else:
            print("Invalid choice. Please try again.")