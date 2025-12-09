import glob
import h5py
import numpy as np

# ----------- CONFIG -------------
DATASETS = {
    "IMC": "../../data_raw/2_days/imc/*.h5",
    "WDP": "../../data_raw/2_days/wdp/*.h5",
    "LST": "../../data_raw/2_days/lst/*.h5",
    "CMP": "../../data_raw/2_days/cmp/*.h5",
    "UTH": "../../data_raw/2_days/uth/*.h5",
    "OLR": "../../data_raw/2_days/olr/*.h5",
    "HEM": "../../data_raw/2_days/hem/*.h5",
}

# These attributes help confirm lat/lon structure.
LAT_KEYS = ["Latitude", "lat", "LAT", "latitude"]
LON_KEYS = ["Longitude", "lon", "LON", "longitude"]

def find_key(h5, possible_keys):
    """Return first matching key inside H5 file."""
    for key in possible_keys:
        if key in h5.keys():
            return key
    return None

def inspect_file(label, path):
    """Inspect one file: dataset keys, shapes, metadata."""
    print("\n" + "=" * 70)
    print(f"DATASET: {label}")
    print("=" * 70)

    files = sorted(glob.glob(path))
    if len(files) == 0:
        print(f"No files found for {label}\n")
        return

    fname = files[0]
    print(f"Using file: {fname}\n")

    with h5py.File(fname, "r") as h:

        # ---- List HDF5 Keys ----
        print("Available Datasets:")
        for k in h.keys():
            print(f"   - {k}")

        print("\nFile Attributes:")
        for a, v in h.attrs.items():
            print(f"   {a} : {v}")

        # ---- Find primary dataset ----
        print("\nDetecting primary data array...")
        main_candidates = [k for k in h.keys() if k not in ["Latitude", "Longitude", "GeoX", "GeoY", "time"]]

        if len(main_candidates) == 1:
            main_key = main_candidates[0]
        else:
            main_key = main_candidates[0]  # pick first if many

        print(f"Primary dataset assumed: {main_key}")

        try:
            arr = h[main_key][:]
            print(f"   Shape: {arr.shape}")
            print(f"   Dtype: {arr.dtype}")
        except Exception as e:
            print("Error reading dataset:", e)

        # ---- Units, Standard name ----
        print("\nDataset Attributes:")
        for a, v in h[main_key].attrs.items():
            print(f"   {a}: {v}")

        # ---- Lat/Lon ----
        lat_key = find_key(h, LAT_KEYS)
        lon_key = find_key(h, LON_KEYS)

        print("\nLat/Lon detection:")
        print(f"   Latitude key : {lat_key}")
        print(f"   Longitude key: {lon_key}")

        if lat_key and lon_key:
            try:
                lat = h[lat_key][:]
                lon = h[lon_key][:]

                print(f"   Lat shape: {lat.shape}")
                print(f"   Lon shape: {lon.shape}")
                print(f"   Lat range: {np.nanmin(lat)}, {np.nanmax(lat)}")
                print(f"   Lon range: {np.nanmin(lon)}, {np.nanmax(lon)}")
            except:
                print("Unable to read lat/lon")

    print("\n" + "-" * 70 + "\n")


if __name__ == "__main__":
    for label, pattern in DATASETS.items():
        inspect_file(label, pattern)
