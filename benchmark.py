"""
Performance Benchmarking and Analysis Script
Run this to analyze model and application performance
"""

import pandas as pd
import numpy as np
import time
import pickle
import os
from datetime import datetime
import json

from performance_utils import (
    perf_monitor, optimize_dataframe_dtypes, 
    GridIndex, vectorized_distance, sample_large_dataset
)
import performance_config as config


def benchmark_data_loading():
    """Benchmark data loading with and without optimizations"""
    print("\n" + "="*70)
    print("BENCHMARK: Data Loading")
    print("="*70)
    
    path = 'data_processed/2_days/finaldata/final_dataset.parquet'
    if not os.path.exists(path):
        print("Dataset not found, skipping benchmark")
        return
    
    # Without optimization
    start = time.time()
    df_unopt = pd.read_parquet(path)
    time_unopt = time.time() - start
    mem_unopt = df_unopt.memory_usage(deep=True).sum() / (1024**2)
    
    print(f"\nWithout Optimization:")
    print(f"  Load Time: {time_unopt:.3f}s")
    print(f"  Memory: {mem_unopt:.2f}MB")
    
    # With optimization
    start = time.time()
    df_opt = pd.read_parquet(path)
    df_opt = optimize_dataframe_dtypes(df_opt)
    time_opt = time.time() - start
    mem_opt = df_opt.memory_usage(deep=True).sum() / (1024**2)
    
    print(f"\nWith Optimization:")
    print(f"  Load Time: {time_opt:.3f}s")
    print(f"  Memory: {mem_opt:.2f}MB")
    
    print(f"\nImprovement:")
    print(f"  Time Saved: {time_unopt - time_opt:.3f}s ({(time_unopt - time_opt) / time_unopt * 100:.1f}%)")
    print(f"  Memory Saved: {mem_unopt - mem_opt:.2f}MB ({(mem_unopt - mem_opt) / mem_unopt * 100:.1f}%)")
    
    return {
        'unoptimized': {'time': time_unopt, 'memory_mb': mem_unopt},
        'optimized': {'time': time_opt, 'memory_mb': mem_opt}
    }


def benchmark_grid_lookup():
    """Benchmark grid lookup with and without spatial indexing"""
    print("\n" + "="*70)
    print("BENCHMARK: Grid Lookup")
    print("="*70)
    
    grid_path = 'data_processed/2_days/grid/grid_definition.parquet'
    if not os.path.exists(grid_path):
        print("Grid not found, skipping benchmark")
        return
    
    grid_df = pd.read_parquet(grid_path)
    print(f"Grid size: {len(grid_df)} cells")
    
    # Test coordinates (10 random locations in India)
    test_coords = [
        (28.6139, 77.2090),  # Delhi
        (19.0760, 72.8777),  # Mumbai
        (12.9716, 77.5946),  # Bangalore
        (22.5726, 88.3639),  # Kolkata
        (13.0827, 80.2707),  # Chennai
        (26.8467, 80.9462),  # Lucknow
        (23.0225, 72.5714),  # Ahmedabad
        (21.1458, 79.0882),  # Nagpur
        (17.3850, 78.4867),  # Hyderabad
        (25.5941, 85.1376),  # Patna
    ]
    
    # Without spatial index (brute force)
    start = time.time()
    for lat, lon in test_coords:
        distances = np.sqrt((grid_df['lat_center'] - lat)**2 + (grid_df['lon_center'] - lon)**2)
        nearest_idx = distances.argmin()
    time_brute = time.time() - start
    
    print(f"\nBrute Force Method:")
    print(f"  Time: {time_brute:.3f}s")
    print(f"  Avg per lookup: {time_brute / len(test_coords) * 1000:.2f}ms")
    
    # With vectorized distance
    start = time.time()
    for lat, lon in test_coords:
        distances = vectorized_distance(lat, lon, 
                                       grid_df['lat_center'].values,
                                       grid_df['lon_center'].values)
        nearest_idx = distances.argmin()
    time_vec = time.time() - start
    
    print(f"\nVectorized Method:")
    print(f"  Time: {time_vec:.3f}s")
    print(f"  Avg per lookup: {time_vec / len(test_coords) * 1000:.2f}ms")
    print(f"  Speedup: {time_brute / time_vec:.1f}x")
    
    # With spatial index
    grid_index = GridIndex(grid_df)
    start = time.time()
    for lat, lon in test_coords:
        result = grid_index.find_nearest(lat, lon)
    time_index = time.time() - start
    
    print(f"\nSpatial Index Method:")
    print(f"  Time: {time_index:.3f}s")
    print(f"  Avg per lookup: {time_index / len(test_coords) * 1000:.2f}ms")
    print(f"  Speedup: {time_brute / time_index:.1f}x")
    
    return {
        'brute_force': time_brute,
        'vectorized': time_vec,
        'spatial_index': time_index,
        'speedup_vec': time_brute / time_vec,
        'speedup_index': time_brute / time_index
    }


def benchmark_prediction():
    """Benchmark prediction performance"""
    print("\n" + "="*70)
    print("BENCHMARK: Model Prediction")
    print("="*70)
    
    model_path = 'models/model_frame_1.pkl'
    if not os.path.exists(model_path):
        print("Model not found, skipping benchmark")
        return
    
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
        model = model_data['model']
        scaler = model_data.get('scaler')
    
    # Create test data (100 samples)
    n_samples = 100
    feature_cols = ['hem', 'wind_speed', 'uth', 'olr', 'lst_k', 'cer', 'cot', 'month', 'day_of_year']
    
    # Random features
    test_data = np.random.rand(n_samples, len(feature_cols))
    test_df = pd.DataFrame(test_data, columns=feature_cols)
    
    if scaler:
        test_data_scaled = scaler.transform(test_df)
    else:
        test_data_scaled = test_data
    
    # Single prediction benchmark
    start = time.time()
    for i in range(n_samples):
        pred = model.predict(test_data_scaled[i:i+1])
    time_single = time.time() - start
    
    print(f"\nSingle Predictions ({n_samples} samples):")
    print(f"  Total Time: {time_single:.3f}s")
    print(f"  Avg per prediction: {time_single / n_samples * 1000:.2f}ms")
    
    # Batch prediction benchmark
    start = time.time()
    pred_batch = model.predict(test_data_scaled)
    time_batch = time.time() - start
    
    print(f"\nBatch Prediction ({n_samples} samples):")
    print(f"  Total Time: {time_batch:.3f}s")
    print(f"  Avg per prediction: {time_batch / n_samples * 1000:.2f}ms")
    print(f"  Speedup: {time_single / time_batch:.1f}x")
    
    return {
        'single': time_single,
        'batch': time_batch,
        'speedup': time_single / time_batch
    }


def benchmark_sampling_strategies():
    """Benchmark different sampling strategies for large datasets"""
    print("\n" + "="*70)
    print("BENCHMARK: Data Sampling Strategies")
    print("="*70)
    
    path = 'data_processed/2_days/finaldata/final_dataset.parquet'
    if not os.path.exists(path):
        print("Dataset not found, skipping benchmark")
        return
    
    df = pd.read_parquet(path)
    print(f"Original dataset: {len(df)} rows, {df.memory_usage(deep=True).sum() / (1024**2):.2f}MB")
    
    # Simple random sampling
    start = time.time()
    sampled_random = df.sample(n=min(5000, len(df)), random_state=42)
    time_random = time.time() - start
    
    print(f"\nRandom Sampling:")
    print(f"  Time: {time_random:.3f}s")
    print(f"  Result: {len(sampled_random)} rows")
    
    # Per-grid sampling (maintains distribution)
    start = time.time()
    sampled_grid = sample_large_dataset(df, per_grid_samples=5)
    time_grid = time.time() - start
    
    print(f"\nPer-Grid Sampling:")
    print(f"  Time: {time_grid:.3f}s")
    print(f"  Result: {len(sampled_grid)} rows")
    
    return {
        'random': {'time': time_random, 'size': len(sampled_random)},
        'per_grid': {'time': time_grid, 'size': len(sampled_grid)}
    }


def run_all_benchmarks():
    """Run all performance benchmarks"""
    print("\n" + "="*70)
    print("PERFORMANCE BENCHMARKING SUITE")
    print("="*70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Config: Caching={config.ENABLE_CACHE}, GridIndex={config.ENABLE_GRID_INDEX}")
    
    results = {}
    
    results['data_loading'] = benchmark_data_loading()
    results['grid_lookup'] = benchmark_grid_lookup()
    results['prediction'] = benchmark_prediction()
    results['sampling'] = benchmark_sampling_strategies()
    
    print("\n" + "="*70)
    print("BENCHMARK SUMMARY")
    print("="*70)
    
    # Save results
    results_file = f'performance_benchmark_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_file}")
    
    return results


if __name__ == "__main__":
    run_all_benchmarks()
