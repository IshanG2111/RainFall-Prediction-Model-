"""
Performance Utilities Module
Provides caching, profiling, and optimization utilities
"""

import time
import functools
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import OrderedDict
import performance_config as config


class LRUCache:
    """Simple LRU cache with TTL support"""
    
    def __init__(self, max_size=100, ttl_seconds=3600):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.timestamps = {}
        
    def get(self, key):
        if key not in self.cache:
            return None
        
        # Check TTL
        if time.time() - self.timestamps[key] > self.ttl_seconds:
            self.remove(key)
            return None
            
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        self.timestamps[key] = time.time()
        
        if len(self.cache) > self.max_size:
            oldest_key = next(iter(self.cache))
            self.remove(oldest_key)
    
    def remove(self, key):
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]
    
    def clear(self):
        self.cache.clear()
        self.timestamps.clear()
    
    def size(self):
        return len(self.cache)


class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.enabled = config.ENABLE_PROFILING
    
    def record(self, operation_name, duration):
        if not self.enabled:
            return
        
        if operation_name not in self.metrics:
            self.metrics[operation_name] = {
                'count': 0,
                'total_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'avg_time': 0
            }
        
        m = self.metrics[operation_name]
        m['count'] += 1
        m['total_time'] += duration
        m['min_time'] = min(m['min_time'], duration)
        m['max_time'] = max(m['max_time'], duration)
        m['avg_time'] = m['total_time'] / m['count']
        
        # Log slow operations
        if config.LOG_SLOW_OPERATIONS and duration > config.SLOW_OPERATION_THRESHOLD:
            print(f"⚠️ Slow operation: {operation_name} took {duration:.2f}s")
    
    def get_stats(self):
        return self.metrics
    
    def print_summary(self):
        if not self.metrics:
            print("No performance metrics collected")
            return
        
        print("\n" + "="*70)
        print("PERFORMANCE SUMMARY")
        print("="*70)
        for op, stats in self.metrics.items():
            print(f"\n{op}:")
            print(f"  Calls: {stats['count']}")
            print(f"  Total Time: {stats['total_time']:.3f}s")
            print(f"  Avg Time: {stats['avg_time']:.3f}s")
            print(f"  Min/Max: {stats['min_time']:.3f}s / {stats['max_time']:.3f}s")
        print("="*70 + "\n")


# Global performance monitor instance
perf_monitor = PerformanceMonitor()


def timed(operation_name=None):
    """Decorator to time function execution"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            perf_monitor.record(op_name, duration)
            return result
        return wrapper
    return decorator


def optimize_dataframe_dtypes(df):
    """Optimize DataFrame memory usage by downcasting numeric types"""
    if not config.OPTIMIZE_DTYPES:
        return df
    
    original_size = df.memory_usage(deep=True).sum() / (1024**2)
    
    for col in df.columns:
        col_type = df[col].dtype
        
        if col_type == 'float64':
            df[col] = pd.to_numeric(df[col], downcast='float')
        elif col_type == 'int64':
            df[col] = pd.to_numeric(df[col], downcast='integer')
    
    optimized_size = df.memory_usage(deep=True).sum() / (1024**2)
    saved = original_size - optimized_size
    
    if saved > 0.1:  # Only log if saved > 100KB
        print(f"Memory optimized: {original_size:.2f}MB → {optimized_size:.2f}MB (saved {saved:.2f}MB)")
    
    return df


def chunked_dataframe_reader(filepath, chunk_size=None):
    """Generator to read DataFrame in chunks for memory efficiency"""
    if chunk_size is None:
        chunk_size = config.CHUNK_SIZE
    
    if filepath.endswith('.parquet'):
        df = pd.read_parquet(filepath)
        for i in range(0, len(df), chunk_size):
            yield df.iloc[i:i+chunk_size]
    elif filepath.endswith('.csv'):
        for chunk in pd.read_csv(filepath, chunksize=chunk_size):
            yield chunk


def vectorized_distance(lat1, lon1, lat_array, lon_array):
    """Fast vectorized distance calculation using numpy"""
    # Simple Euclidean distance (for small areas)
    # For more accuracy with lat/lon, use haversine but this is faster
    lat_diff = lat_array - lat1
    lon_diff = lon_array - lon1
    return np.sqrt(lat_diff**2 + lon_diff**2)


class GridIndex:
    """Spatial index for fast grid lookups"""
    
    def __init__(self, grid_df):
        self.grid_df = grid_df
        self.lat_bins = None
        self.lon_bins = None
        self.grid_hash = {}
        self._build_index()
    
    def _build_index(self):
        """Build spatial hash index"""
        # Create hash map based on rounded coordinates
        for idx, row in self.grid_df.iterrows():
            lat_key = round(row['lat_center'] * 4) / 4  # 0.25 degree bins
            lon_key = round(row['lon_center'] * 4) / 4
            key = (lat_key, lon_key)
            
            if key not in self.grid_hash:
                self.grid_hash[key] = []
            self.grid_hash[key].append(idx)
    
    def find_nearest(self, lat, lon, max_candidates=9):
        """Find nearest grid cell using spatial index"""
        lat_key = round(lat * 4) / 4
        lon_key = round(lon * 4) / 4
        
        # Get candidates from this bin and adjacent bins
        candidates = []
        for lat_offset in [-0.25, 0, 0.25]:
            for lon_offset in [-0.25, 0, 0.25]:
                key = (lat_key + lat_offset, lon_key + lon_offset)
                if key in self.grid_hash:
                    candidates.extend(self.grid_hash[key])
        
        if not candidates:
            # Fallback to full search
            return self._full_search(lat, lon)
        
        # Calculate distances only for candidates
        candidate_grid = self.grid_df.iloc[candidates]
        distances = vectorized_distance(
            lat, lon,
            candidate_grid['lat_center'].values,
            candidate_grid['lon_center'].values
        )
        
        nearest_idx = candidates[np.argmin(distances)]
        return self.grid_df.iloc[nearest_idx]
    
    def _full_search(self, lat, lon):
        """Fallback to full grid search"""
        distances = vectorized_distance(
            lat, lon,
            self.grid_df['lat_center'].values,
            self.grid_df['lon_center'].values
        )
        nearest_idx = distances.argmin()
        return self.grid_df.iloc[nearest_idx]


def sample_large_dataset(df, sample_ratio=None, per_grid_samples=None):
    """
    Sample a large dataset efficiently while maintaining grid distribution
    """
    if sample_ratio is None:
        sample_ratio = config.SAMPLE_SIZE_RATIO
    if per_grid_samples is None:
        per_grid_samples = config.MIN_SAMPLES_PER_GRID
    
    # If dataset is small enough, return as-is
    if len(df) < config.CHUNK_SIZE * 2:
        return df
    
    # Sample per grid to maintain distribution
    if 'grid_id' in df.columns:
        sampled = df.groupby('grid_id').apply(
            lambda x: x.sample(n=min(per_grid_samples, len(x)), random_state=42)
        ).reset_index(drop=True)
        print(f"Sampled dataset: {len(df)} → {len(sampled)} rows (per-grid sampling)")
        return sampled
    else:
        # Simple random sampling
        n_samples = max(1000, int(len(df) * sample_ratio))
        sampled = df.sample(n=n_samples, random_state=42)
        print(f"Sampled dataset: {len(df)} → {len(sampled)} rows (random sampling)")
        return sampled


def create_performance_report(monitor=None):
    """Generate a performance analysis report"""
    if monitor is None:
        monitor = perf_monitor
    
    stats = monitor.get_stats()
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_operations': sum(s['count'] for s in stats.values()),
        'total_time': sum(s['total_time'] for s in stats.values()),
        'operations': stats
    }
    
    return report
