import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import glob
import geopandas as gpd
from shapely.geometry import Point

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 120
plt.rcParams["savefig.dpi"] = 300

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_ROOT = PROJECT_ROOT / "data_processed" / "3_months"
MASTER_DAILY_DIR = PROCESSED_ROOT / "master_daily"
FINAL_DATASET_PATH = PROCESSED_ROOT / "final_dataset" / "final_dataset.parquet"
GRID_PATH = PROJECT_ROOT / "grid" / "grid_definition.parquet"
FIGURES_DIR = PROJECT_ROOT / "reports" / "data_preprocessing"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def load_master_data():
    files = sorted(glob.glob(str(MASTER_DAILY_DIR / "master_raw_*.parquet")))
    dfs = [pd.read_parquet(f) for f in files]
    return pd.concat(dfs, ignore_index=True)

def load_final_data():
    return pd.read_parquet(FINAL_DATASET_PATH)

def load_grid():
    return pd.read_parquet(GRID_PATH)

def load_india_map():
    shapefile_path = PROJECT_ROOT / "maps" / "ne_110m_admin_0_countries.shp"
    world = gpd.read_file(shapefile_path)
    india = world[world["ADMIN"] == "India"]
    return india

def plot_missing_values():
    before_df = load_master_data()
    after_df = load_final_data()
    before_missing = before_df.isnull().sum()
    after_missing = after_df.isnull().sum()
    df = pd.DataFrame({"Before": before_missing,"After": after_missing}).fillna(0)
    df = df[df.sum(axis=1) > 0]
    plt.figure(figsize=(12, 6))
    df.plot(kind="bar", width=0.8, edgecolor="black")
    plt.title("Missing Values Before vs After Imputation", fontsize=14)
    plt.xlabel("Features")
    plt.ylabel("Missing Count")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "missing_values.png")
    plt.close()

def plot_grid():
    grid_df = load_grid()
    india = load_india_map()
    geometry = [Point(xy) for xy in zip(grid_df["lon_center"], grid_df["lat_center"])]
    gdf = gpd.GeoDataFrame(grid_df, geometry=geometry, crs="EPSG:4326")
    gdf = gpd.clip(gdf, india)
    plt.figure(figsize=(8, 10))
    india.plot(color="white", edgecolor="black")
    gdf.plot(markersize=1,color="blue",alpha=0.6,label="Grid Points")
    plt.title("Spatial Grid Mapping over India", fontsize=14)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "grid_visualization_map.png")
    plt.close()

def plot_feature_distribution():
    df = load_final_data()
    features = ["rain_mm", "lst_k", "wind_speed", "uth", "olr"]
    plt.figure(figsize=(15, 10))
    for i, col in enumerate(features, 1):
        if col in df.columns:
            plt.subplot(2, 3, i)
            sns.histplot(df[col].dropna(), kde=True, bins=40, color="skyblue")
            plt.title(f"{col} Distribution")
            plt.xlabel(col)
            plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "feature_distribution.png")
    plt.close()

def plot_correlation_heatmap():
    df = load_final_data()
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr,annot=True,cmap="coolwarm",fmt=".2f",linewidths=0.5,square=True,cbar_kws={"shrink": 0.8})
    plt.title("Feature Correlation Heatmap", fontsize=14)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "correlation_heatmap.png")
    plt.close()

def plot_temporal_trends():
    df = load_final_data()
    df["date"] = pd.to_datetime(df["date"])
    daily_rain = df.groupby("date")["rain_mm"].mean()
    plt.figure(figsize=(12, 6))
    plt.plot(daily_rain.index, daily_rain.values, color="green", linewidth=2)
    plt.title("Average Daily Rainfall Over Time", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Rainfall (mm)")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "temporal_trend.png")
    plt.close()

def plot_spatial_heatmap():
    df = load_final_data()
    india = load_india_map()
    df["date"] = pd.to_datetime(df["date"])
    spatial_avg = df.groupby(["lat_center", "lon_center"])["rain_mm"].mean().reset_index()
    geometry = [Point(xy) for xy in zip(spatial_avg["lon_center"], spatial_avg["lat_center"])]
    gdf = gpd.GeoDataFrame(spatial_avg, geometry=geometry, crs="EPSG:4326")
    gdf = gpd.clip(gdf, india)
    plt.figure(figsize=(8, 10))
    india.plot(color="lightgrey", edgecolor="black")
    gdf.plot(column="rain_mm",cmap="turbo",markersize=8,legend=True,alpha=0.9)
    plt.title("Spatial Rainfall Distribution over India", fontsize=14)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "spatial_heatmap_map.png")
    plt.close()

def run_all_plots():
    print("Generating plots\n")
    plot_missing_values()
    print("Missing values")
    plot_grid()
    print("Grid map")
    plot_feature_distribution()
    print("Feature distribution")
    plot_correlation_heatmap()
    print("Correlation heatmap")
    plot_temporal_trends()
    print("Temporal trends")
    plot_spatial_heatmap()
    print("Spatial heatmap")
    print("\nAll plots saved in:", FIGURES_DIR)

if __name__ == "__main__":
    run_all_plots()