"""
Performance Demo Script
Run this to see a live demonstration of the performance improvements
"""

import time
import numpy as np
import pandas as pd
from performance_utils import timed, perf_monitor, optimize_dataframe_dtypes, GridIndex
import performance_config as config

def demo_memory_optimization():
    """Demonstrate memory optimization"""
    print("\n" + "="*70)
    print("DEMO 1: Memory Optimization")
    print("="*70)
    
    # Create a sample dataset
    size = 10000
    df = pd.DataFrame({
        'temperature': np.random.randn(size).astype('float64'),
        'pressure': np.random.randn(size).astype('float64'),
        'humidity': np.random.randn(size).astype('float64'),
        'wind_speed': np.random.randn(size).astype('float64'),
        'grid_id': np.random.randint(1, 1000, size).astype('int64'),
        'day': np.random.randint(1, 365, size).astype('int64')
    })
    
    mem_before = df.memory_usage(deep=True).sum() / 1024
    print(f"\nBefore optimization:")
    print(f"  Rows: {len(df):,}")
    print(f"  Memory: {mem_before:.1f} KB")
    print(f"  Data types: {dict(df.dtypes)}")
    
    df_opt = optimize_dataframe_dtypes(df)
    mem_after = df_opt.memory_usage(deep=True).sum() / 1024
    
    print(f"\nAfter optimization:")
    print(f"  Memory: {mem_after:.1f} KB")
    print(f"  Savings: {mem_before - mem_after:.1f} KB ({(mem_before - mem_after) / mem_before * 100:.1f}%)")
    print(f"  Data types: {dict(df_opt.dtypes)}")


def demo_grid_lookup_speed():
    """Demonstrate grid lookup speed improvements"""
    print("\n" + "="*70)
    print("DEMO 2: Grid Lookup Speed")
    print("="*70)
    
    # Create sample grid
    lats = np.arange(10, 30, 0.25)
    lons = np.arange(70, 90, 0.25)
    grid_data = []
    grid_id = 1
    for lat in lats:
        for lon in lons:
            grid_data.append({'grid_id': grid_id, 'lat_center': lat, 'lon_center': lon})
            grid_id += 1
    
    grid_df = pd.DataFrame(grid_data)
    print(f"\nGrid size: {len(grid_df):,} cells")
    
    # Test locations (major cities)
    test_locations = [
        (28.6139, 77.2090, "Delhi"),
        (19.0760, 72.8777, "Mumbai"),
        (12.9716, 77.5946, "Bangalore"),
        (22.5726, 88.3639, "Kolkata"),
        (13.0827, 80.2707, "Chennai")
    ]
    
    # Method 1: Brute force
    print("\nMethod 1: Brute Force Search")
    start = time.time()
    for lat, lon, city in test_locations:
        distances = np.sqrt((grid_df['lat_center'] - lat)**2 + (grid_df['lon_center'] - lon)**2)
        nearest_idx = distances.argmin()
    time_brute = time.time() - start
    print(f"  Time: {time_brute*1000:.2f} ms ({time_brute*1000/len(test_locations):.2f} ms per lookup)")
    
    # Method 2: With spatial index
    print("\nMethod 2: Spatial Index")
    grid_index = GridIndex(grid_df)
    start = time.time()
    for lat, lon, city in test_locations:
        result = grid_index.find_nearest(lat, lon)
    time_index = time.time() - start
    print(f"  Time: {time_index*1000:.2f} ms ({time_index*1000/len(test_locations):.2f} ms per lookup)")
    print(f"  Speedup: {time_brute/time_index:.1f}x faster")


def demo_batch_vs_single():
    """Demonstrate batch processing benefits"""
    print("\n" + "="*70)
    print("DEMO 3: Batch vs Single Predictions")
    print("="*70)
    
    # Simulate model predictions
    def fake_model_predict(data):
        """Simulate model prediction with some overhead"""
        time.sleep(0.001)  # Simulate processing time
        return np.random.rand(len(data))
    
    n_predictions = 50
    features = np.random.rand(n_predictions, 9)
    
    # Method 1: Single predictions
    print(f"\nPredicting {n_predictions} samples...")
    print("\nMethod 1: Single Predictions")
    start = time.time()
    results = []
    for i in range(n_predictions):
        pred = fake_model_predict(features[i:i+1])
        results.append(pred[0])
    time_single = time.time() - start
    print(f"  Time: {time_single*1000:.2f} ms ({time_single*1000/n_predictions:.2f} ms per prediction)")
    
    # Method 2: Batch prediction
    print("\nMethod 2: Batch Prediction")
    start = time.time()
    results_batch = fake_model_predict(features)
    time_batch = time.time() - start
    print(f"  Time: {time_batch*1000:.2f} ms ({time_batch*1000/n_predictions:.2f} ms per prediction)")
    print(f"  Speedup: {time_single/time_batch:.1f}x faster")


def demo_caching_benefits():
    """Demonstrate caching benefits"""
    print("\n" + "="*70)
    print("DEMO 4: Caching Benefits")
    print("="*70)
    
    from performance_utils import LRUCache
    
    cache = LRUCache(max_size=10, ttl_seconds=60)
    
    def expensive_operation(key):
        """Simulate expensive computation"""
        time.sleep(0.01)  # 10ms operation
        return f"result_for_{key}"
    
    test_keys = ['key1', 'key2', 'key3', 'key1', 'key2', 'key3', 'key1', 'key2']
    
    print(f"\nProcessing {len(test_keys)} requests...")
    print("Keys:", test_keys)
    
    # Without cache
    print("\nWithout Cache:")
    start = time.time()
    results = []
    for key in test_keys:
        result = expensive_operation(key)
        results.append(result)
    time_no_cache = time.time() - start
    print(f"  Time: {time_no_cache*1000:.2f} ms")
    
    # With cache
    print("\nWith Cache:")
    start = time.time()
    results_cached = []
    cache_hits = 0
    cache_misses = 0
    for key in test_keys:
        cached = cache.get(key)
        if cached:
            results_cached.append(cached)
            cache_hits += 1
        else:
            result = expensive_operation(key)
            cache.put(key, result)
            results_cached.append(result)
            cache_misses += 1
    time_with_cache = time.time() - start
    print(f"  Time: {time_with_cache*1000:.2f} ms")
    print(f"  Cache hits: {cache_hits}/{len(test_keys)} ({cache_hits/len(test_keys)*100:.1f}%)")
    print(f"  Cache misses: {cache_misses}/{len(test_keys)}")
    print(f"  Speedup: {time_no_cache/time_with_cache:.1f}x faster")


def main():
    print("\n" + "="*70)
    print("PERFORMANCE OPTIMIZATION DEMONSTRATION")
    print("="*70)
    print(f"Configuration:")
    print(f"  Caching: {config.ENABLE_CACHE}")
    print(f"  Grid Index: {config.ENABLE_GRID_INDEX}")
    print(f"  Profiling: {config.ENABLE_PROFILING}")
    
    demo_memory_optimization()
    demo_grid_lookup_speed()
    demo_batch_vs_single()
    demo_caching_benefits()
    
    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)
    
    if config.ENABLE_PROFILING:
        print("\nPerformance Summary:")
        perf_monitor.print_summary()


if __name__ == "__main__":
    main()
