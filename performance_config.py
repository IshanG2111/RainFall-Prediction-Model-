"""
Performance Configuration Module
Centralized configuration for memory limits, batch sizes, and caching settings
"""

# Memory and Performance Settings
MAX_MEMORY_MB = 500  # Maximum memory to use for dataset cache
CHUNK_SIZE = 5000  # Rows to process at a time for large datasets
BATCH_SIZE = 100  # Maximum locations to process in one batch prediction

# Caching Settings
ENABLE_CACHE = True
CACHE_TTL_SECONDS = 3600  # 1 hour cache lifetime
MAX_CACHE_ENTRIES = 1000  # Maximum number of cached predictions

# Grid Optimization
ENABLE_GRID_INDEX = True  # Use spatial indexing for grid lookups
GRID_CACHE_SIZE = 500  # Number of grid lookups to cache

# Feature Sampling
SAMPLE_SIZE_RATIO = 0.1  # Use 10% of data for feature sampling (for huge datasets)
MIN_SAMPLES_PER_GRID = 5  # Minimum samples to keep per grid cell

# Data Loading
USE_LAZY_LOADING = True  # Load data only when needed
OPTIMIZE_DTYPES = True  # Convert to smaller data types to save memory

# Model Settings
ENABLE_MODEL_OPTIMIZATION = True  # Use optimized model settings
USE_INCREMENTAL_LEARNING = False  # Enable incremental learning for huge datasets
MAX_LEAF_NODES = 31  # Limit tree complexity (powers of 2 minus 1 are optimal)

# Performance Monitoring
ENABLE_PROFILING = True  # Enable performance profiling
LOG_SLOW_OPERATIONS = True  # Log operations taking >1 second
SLOW_OPERATION_THRESHOLD = 1.0  # Seconds
MEMORY_LOG_THRESHOLD_KB = 100  # Log memory savings above this threshold (KB)
