from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PHASE_CONFIG = {
    "2_days": {
        "dates":["15JUL2025","16JUL2025"],
        "raw_base_dir":PROJECT_ROOT/"data_raw"/"2_days",
        "processed_base_dir":PROJECT_ROOT/"data_processed"/"2_days",
    },
    "8_days": {
        "dates":["15JAN2025","21MAY2025","10JUN2025","20JUL2025","25JUL2025","15AUG2025","20SEP2025","10NOV2025"],
        "raw_base_dir":PROJECT_ROOT/"data_raw"/"8_days",
        "processed_base_dir":PROJECT_ROOT/"data_processed"/"8_days",
    },
}
