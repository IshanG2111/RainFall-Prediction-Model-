from scripts.config.phase_config import PHASE_CONFIG
from scripts.merge_data.merge_feature import merge_all_daily

def run_merge_daily(phase_name: str):
    if phase_name not in PHASE_CONFIG:
        raise ValueError(f"Phase '{phase_name}' not found in PHASE_CONFIG")

    cfg = PHASE_CONFIG[phase_name]
    dates = cfg["dates"]
    processed_base_dir = cfg["processed_base_dir"]

    print(f"\nStarting DAILY MERGE for phase: {phase_name}")
    print(f"Total days: {len(dates)}")

    for d in dates:
        print(f"Merging daily files for date: {d}")
        merge_all_daily(date_str=d,processed_base_dir=processed_base_dir,save=True)

    print("\nAll daily merge tasks completed successfully!")

if __name__ == "__main__":
    while True:
        print("\nDAILY MERGE MENU")
        print("1. Run 2_days merge")
        print("2. Run 8_days merge")
        print("3. Run 3_months merge")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ").strip()
        if choice == "1":
            run_merge_daily("2_days")
        elif choice == "2":
            run_merge_daily("8_days")
        elif choice == "3":
            run_merge_daily("3_months")
        elif choice == "4":
            print("Exiting daily merge pipeline.")
            break
        else:
            print("Invalid choice. Please try again.")