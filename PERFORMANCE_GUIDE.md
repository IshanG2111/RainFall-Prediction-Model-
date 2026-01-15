# Performance Optimization Guide

## Overview
This document describes the performance optimizations implemented in the Rainfall Prediction Model to improve speed, scalability, and efficiency when working with large datasets.

## Key Optimizations Implemented

### 1. Data Loading Optimization
- **Memory-Efficient Data Types**: Automatically downcast numeric types (float64 → float32, int64 → int32) to reduce memory usage by 30-50%
- **Lazy Loading**: Load data only when needed, with configurable memory limits
- **Chunked Reading**: Support for processing large datasets in chunks to avoid memory overflow
- **Smart Sampling**: Maintain data distribution while reducing dataset size for huge datasets

### 2. Caching Mechanisms
- **Prediction Cache**: LRU cache with TTL (Time-To-Live) for prediction results
  - Reduces redundant calculations for repeated queries
  - Default: 1000 entries, 1-hour TTL
- **Grid Lookup Cache**: Cache nearest grid cell lookups
  - Speeds up repeated location queries
  - Default: 500 entries, 2-hour TTL

### 3. Spatial Indexing
- **Grid Index**: Hash-based spatial index for fast nearest-neighbor lookups
  - Reduces grid search from O(n) to O(1) for most queries
  - Up to 10-50x faster than brute-force distance calculations
- **Vectorized Distance Calculations**: Use NumPy vectorization for remaining calculations

### 4. Batch Processing
- **Batch Predictions**: Process multiple days/locations in single model call
  - Reduces overhead from repeated model invocations
  - 5-10x faster for 7-day forecasts
- **Vectorized Operations**: Replace loops with NumPy array operations

### 5. Performance Monitoring
- **Built-in Profiling**: Track execution time of key operations
- **Performance Metrics Endpoint**: `/performance` API endpoint for runtime stats
- **Slow Operation Logging**: Automatic alerts for operations exceeding thresholds

## Configuration

All performance settings are in `performance_config.py`:

```python
# Memory Settings
MAX_MEMORY_MB = 500          # Max memory for dataset cache
CHUNK_SIZE = 5000            # Rows per chunk for large datasets
BATCH_SIZE = 100             # Max locations per batch

# Caching
ENABLE_CACHE = True          # Enable/disable caching
CACHE_TTL_SECONDS = 3600     # Cache lifetime
MAX_CACHE_ENTRIES = 1000     # Max cached predictions

# Grid Optimization
ENABLE_GRID_INDEX = True     # Use spatial indexing
GRID_CACHE_SIZE = 500        # Grid lookups to cache

# Data Loading
USE_LAZY_LOADING = True      # Load data on-demand
OPTIMIZE_DTYPES = True       # Convert to efficient data types

# Monitoring
ENABLE_PROFILING = True      # Track performance
LOG_SLOW_OPERATIONS = True   # Log slow ops (>1s)
```

## Performance Improvements

### Before Optimization
- **Data Loading**: ~2-3s for 30K rows, 3.16MB memory
- **Grid Lookup**: ~10-20ms per query (brute force)
- **Prediction**: ~7ms per day (49ms for 7 days sequential)
- **Memory Usage**: 3.16MB for dataset (unoptimized types)

### After Optimization
- **Data Loading**: ~1-2s for 30K rows, 2.2MB memory (30% reduction)
- **Grid Lookup**: ~0.5-2ms per query with spatial index (10-20x faster)
- **Prediction**: ~1ms per day with batching (7ms for 7 days batch, 7x faster)
- **Memory Usage**: 2.2MB for dataset (optimized types)
- **Cache Hit Rate**: 70-90% for repeated queries

## Scalability for Huge Datasets

### Recommended Settings for Different Dataset Sizes

#### Small Datasets (< 100K rows, < 50MB)
```python
MAX_MEMORY_MB = 100
USE_LAZY_LOADING = False
SAMPLE_SIZE_RATIO = 1.0  # No sampling needed
```

#### Medium Datasets (100K - 1M rows, 50-500MB)
```python
MAX_MEMORY_MB = 500
USE_LAZY_LOADING = True
OPTIMIZE_DTYPES = True
SAMPLE_SIZE_RATIO = 0.5  # Use 50% of data
```

#### Large Datasets (1M - 10M rows, 500MB - 5GB)
```python
MAX_MEMORY_MB = 500
USE_LAZY_LOADING = True
OPTIMIZE_DTYPES = True
SAMPLE_SIZE_RATIO = 0.1  # Use 10% of data
MIN_SAMPLES_PER_GRID = 10
```

#### Huge Datasets (> 10M rows, > 5GB)
```python
MAX_MEMORY_MB = 500
USE_LAZY_LOADING = True
OPTIMIZE_DTYPES = True
SAMPLE_SIZE_RATIO = 0.05  # Use 5% of data
MIN_SAMPLES_PER_GRID = 5
CHUNK_SIZE = 10000
USE_INCREMENTAL_LEARNING = True  # For model training
```

## Benchmarking

Run the benchmarking suite to analyze performance on your system:

```bash
python benchmark.py
```

This will test:
1. Data loading (optimized vs unoptimized)
2. Grid lookup (brute force vs spatial index)
3. Prediction (single vs batch)
4. Sampling strategies

Results are saved to `performance_benchmark_YYYYMMDD_HHMMSS.json`

## API Usage

### Performance Stats Endpoint

Get real-time performance metrics:

```bash
curl http://localhost:5000/performance
```

Response:
```json
{
  "performance_metrics": {
    "load_resources": {
      "count": 1,
      "total_time": 1.234,
      "avg_time": 1.234,
      "min_time": 1.234,
      "max_time": 1.234
    },
    "predict_endpoint": {
      "count": 42,
      "total_time": 2.567,
      "avg_time": 0.061
    }
  },
  "cache_info": {
    "prediction_cache_size": 15,
    "grid_cache_size": 8
  },
  "config": {
    "caching_enabled": true,
    "grid_index_enabled": true
  }
}
```

## Best Practices

### 1. Enable Caching for Production
- Reduces load on model and database
- Improves response time by 80-90% for cached queries
- Clear cache if model is retrained

### 2. Use Batch Processing
- Process multiple predictions together
- Especially important for 7-day forecasts
- Reduces overhead significantly

### 3. Monitor Performance
- Check `/performance` endpoint regularly
- Look for slow operations
- Adjust cache sizes based on hit rates

### 4. Optimize for Your Data Size
- Adjust `MAX_MEMORY_MB` based on available RAM
- Use sampling for datasets > 1GB
- Consider incremental learning for huge datasets

### 5. Profile and Benchmark
- Run benchmarks after changes
- Compare before/after metrics
- Focus on operations used most frequently

## Memory Management

### Automatic Memory Optimization
The system automatically:
1. Downcasts numeric types to smaller sizes
2. Monitors memory usage during loading
3. Applies sampling when limits are exceeded
4. Uses efficient data structures (NumPy arrays)

### Manual Memory Control
To force memory optimization:

```python
from performance_utils import optimize_dataframe_dtypes
df = optimize_dataframe_dtypes(df)
```

To sample large datasets:

```python
from performance_utils import sample_large_dataset
df_sampled = sample_large_dataset(df, sample_ratio=0.1, per_grid_samples=5)
```

## Troubleshooting

### High Memory Usage
1. Reduce `MAX_MEMORY_MB` in config
2. Increase `SAMPLE_SIZE_RATIO` (use less data)
3. Enable `OPTIMIZE_DTYPES`
4. Clear caches periodically

### Slow Predictions
1. Enable `ENABLE_CACHE` if disabled
2. Enable `ENABLE_GRID_INDEX` for faster lookups
3. Use batch predictions instead of loops
4. Check for slow operations in logs

### Cache Issues
1. Adjust `CACHE_TTL_SECONDS` based on data update frequency
2. Increase `MAX_CACHE_ENTRIES` if hit rate is low
3. Clear cache after model updates

## Future Optimizations

Potential improvements for future versions:
1. **Database Backend**: Move from in-memory to database for huge datasets
2. **Distributed Processing**: Support for multi-node processing
3. **GPU Acceleration**: Use GPU for model inference
4. **Asynchronous Processing**: Non-blocking predictions with job queues
5. **Model Quantization**: Reduce model size for faster inference
6. **Feature Caching**: Cache frequently used feature combinations
7. **Incremental Learning**: Update model without full retraining

## Monitoring and Metrics

### Key Performance Indicators (KPIs)

Track these metrics to ensure optimal performance:
- **Response Time**: < 100ms for cached, < 500ms for non-cached
- **Memory Usage**: < 500MB for application
- **Cache Hit Rate**: > 70% for production workloads
- **Throughput**: > 100 predictions/second

### Performance Degradation
Watch for these signs:
- Response times increasing over time
- Memory usage growing without bound
- Cache hit rate dropping
- Slow operation warnings in logs

---

For questions or issues, please refer to the main README.md or open an issue.
