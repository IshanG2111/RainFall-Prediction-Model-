from scripts.config.phase_config import PHASE_CONFIG
from scripts.grid.grid_loader import load_grid_definition
from scripts.features.imc_daily import process_imc_daily
from scripts.features.wdp_daily import process_wdp_daily
from scripts.features.lst_daily import process_lst_daily
from scripts.features.cmp_daily import process_cmp_daily
from scripts.features.uth_daily import process_uth_daily
from scripts.features.olr_daily import process_olr_daily
from scripts.features.hem_daily import process_hem_daily

def build_file_index(raw_dir, feature):
    import glob
    import os

    files = glob.glob(f"{raw_dir}/{feature}/*.h5")

    file_map = {}

    for fp in files:
        fname = os.path.basename(fp)
        date = fname[6:15]

        file_map.setdefault(date, []).append(fp)

    return file_map

def run_daily_aggregation(phase_name: str):
    if phase_name not in PHASE_CONFIG:
        raise ValueError(f"Phase '{phase_name}' not found in PHASE_CONFIG")

    cfg = PHASE_CONFIG[phase_name]
    dates = cfg["dates"]

    features = ["imc"]   # later add: "wdp", "lst", "cmp"

    grid_df = load_grid_definition()

    file_maps = {}

    for feature in features:
        print(f"Building file index for {feature}...")
        file_maps[feature] = build_file_index(cfg["raw_base_dir"], feature)

    print(f"\nStarting DAILY AGGREGATION for phase: {phase_name}")
    print(f"Total days: {len(dates)}")

    for d in dates:
        print(f"\nProcessing date: {d}")
        process_imc_daily(d, cfg, grid_df, file_maps["imc"])
        # process_wdp_daily(d, cfg, grid_df, file_maps["wdp"])
        # process_lst_daily(d, cfg, grid_df, file_maps["lst"])
        # process_cmp_daily(d, cfg, grid_df, file_maps["cmp"])
        # process_uth_daily(d, cfg, grid_df)
        # process_olr_daily(d, cfg, grid_df)
        # process_hem_daily(d, cfg, grid_df)

    print("\nAll daily aggregation tasks completed successfully!")

if __name__ == "__main__":
    run_daily_aggregation("3_years")