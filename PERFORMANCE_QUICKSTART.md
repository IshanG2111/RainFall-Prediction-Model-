# Performance Optimization Quick Reference

## Quick Start

### Run Benchmarks
```bash
python benchmark.py
```

### See Live Demo
```bash
python performance_demo.py
```

### Train Model (with monitoring)
```bash
python model.py
```

### Start Application (with optimizations)
```bash
python app.py
# Access at http://localhost:5000
# View performance stats at http://localhost:5000/performance
```

## Configuration Quick Reference

Edit `performance_config.py`:

### For Production (Recommended)
```python
MAX_MEMORY_MB = 500
ENABLE_CACHE = True
ENABLE_GRID_INDEX = True
USE_LAZY_LOADING = True
OPTIMIZE_DTYPES = True
ENABLE_PROFILING = True
```

### For Large Datasets (>1GB)
```python
MAX_MEMORY_MB = 500
SAMPLE_SIZE_RATIO = 0.1  # Use 10% of data
MIN_SAMPLES_PER_GRID = 5
USE_LAZY_LOADING = True
```

### For Development/Debugging
```python
MAX_MEMORY_MB = 200
ENABLE_CACHE = False  # See real performance
ENABLE_PROFILING = True
LOG_SLOW_OPERATIONS = True
```

## Performance Metrics

### Key Improvements
| Feature | Before | After | Improvement |
|---------|--------|-------|-------------|
| Data Loading | 0.023s | 0.010s | **55.9% faster** |
| Memory Usage | 3.16 MB | 1.99 MB | **37% less** |
| Grid Lookup | 0.37 ms | 0.06 ms | **5.8x faster** |
| Predictions | 3.74 ms | 0.04 ms | **85x faster** |

### API Performance
- **Response Time**: 5-15ms (with cache: 1-2ms)
- **Throughput**: 100+ predictions/second
- **Cache Hit Rate**: 70-90% (typical)

## Common Tasks

### Monitor Performance
```python
from performance_utils import perf_monitor

# After running operations
perf_monitor.print_summary()
```

### Clear Cache
```python
from app import prediction_cache, grid_cache

if prediction_cache:
    prediction_cache.clear()
if grid_cache:
    grid_cache.clear()
```

### Optimize DataFrame
```python
from performance_utils import optimize_dataframe_dtypes

df = pd.read_parquet('data.parquet')
df = optimize_dataframe_dtypes(df)  # Saves 30-50% memory
```

### Use Spatial Index
```python
from performance_utils import GridIndex

grid_index = GridIndex(grid_df)
result = grid_index.find_nearest(lat, lon)  # Fast lookup
```

### Time Operations
```python
from performance_utils import timed

@timed('my_operation')
def my_function():
    # Your code here
    pass
```

## Troubleshooting

### Problem: High memory usage
**Solution**: 
1. Reduce `MAX_MEMORY_MB` in config
2. Increase `SAMPLE_SIZE_RATIO` 
3. Enable `OPTIMIZE_DTYPES`

### Problem: Slow predictions
**Solution**:
1. Enable `ENABLE_CACHE`
2. Use batch predictions
3. Enable `ENABLE_GRID_INDEX`

### Problem: Cache not helping
**Solution**:
1. Increase `MAX_CACHE_ENTRIES`
2. Increase `CACHE_TTL_SECONDS`
3. Check cache hit rate at `/performance`

### Problem: Out of memory
**Solution**:
1. Set `MAX_MEMORY_MB = 500`
2. Set `SAMPLE_SIZE_RATIO = 0.05` (5%)
3. Set `MIN_SAMPLES_PER_GRID = 3`
4. Enable `USE_LAZY_LOADING = True`

## File Reference

- `performance_config.py` - All configuration settings
- `performance_utils.py` - Optimization utilities
- `benchmark.py` - Run performance tests
- `performance_demo.py` - See live demonstrations
- `PERFORMANCE_GUIDE.md` - Detailed documentation
- `PERFORMANCE_ANALYSIS.md` - Benchmark results

## API Endpoints

### Get Performance Stats
```bash
curl http://localhost:5000/performance
```

### Make Prediction
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"city": "Delhi", "date": "2025-07-15"}'
```

## Best Practices

1. ✅ Always enable caching in production
2. ✅ Use batch predictions when possible
3. ✅ Monitor performance regularly
4. ✅ Optimize data types before processing
5. ✅ Use spatial indexing for lookups
6. ✅ Configure based on dataset size
7. ✅ Clear cache after model retraining

## Scalability Guidelines

### Dataset Size Guide
- **Small (<100K rows)**: Use default settings
- **Medium (100K-1M)**: Enable sampling (50%)
- **Large (1M-10M)**: Enable sampling (10%)
- **Huge (>10M)**: Enable sampling (5%), chunking

### Memory Guidelines
- **4GB RAM**: MAX_MEMORY_MB = 200
- **8GB RAM**: MAX_MEMORY_MB = 500
- **16GB+ RAM**: MAX_MEMORY_MB = 1000

## Performance Monitoring

### Track Operations
```python
from performance_utils import perf_monitor

stats = perf_monitor.get_stats()
print(stats)
```

### View in API
```bash
# Real-time stats
curl http://localhost:5000/performance | jq
```

### Expected Metrics
- load_resources: ~1s
- predict_endpoint: 5-15ms
- find_nearest_grid: <1ms
- get_realistic_features: <1ms

## Support

For detailed documentation, see:
- [PERFORMANCE_GUIDE.md](PERFORMANCE_GUIDE.md) - Complete guide
- [PERFORMANCE_ANALYSIS.md](PERFORMANCE_ANALYSIS.md) - Benchmark data
- [README.md](README.md) - Main documentation
