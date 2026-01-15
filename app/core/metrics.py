"""Prometheus metrics for DocC2Context Service monitoring"""

from prometheus_client import Counter, Gauge, Histogram

# HTTP Request Metrics
request_count = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10),
)

# ZIP Extraction Metrics
zip_extractions_total = Counter(
    "zip_extractions_total",
    "Total ZIP extractions attempted",
    ["status"],  # success, failed_validation, failed_extraction
)

zip_extraction_duration = Histogram(
    "zip_extraction_duration_seconds",
    "ZIP extraction duration in seconds",
    buckets=(0.1, 0.5, 1, 2, 5, 10, 30),
)

extraction_file_count = Histogram(
    "extraction_file_count",
    "Number of files extracted per ZIP",
    buckets=(1, 10, 100, 1000, 10000),
)

extraction_size_bytes = Histogram(
    "extraction_size_bytes",
    "Size of extracted content in bytes",
    buckets=(1024, 10485760, 104857600, 1073741824),  # 1KB, 10MB, 100MB, 1GB
)

# Conversion Activity Metrics
active_conversions = Gauge(
    "active_conversions",
    "Number of active conversions",
)

conversion_errors_total = Counter(
    "conversion_errors_total",
    "Total conversion errors",
    ["error_type"],  # validation_error, extraction_error, cli_error, timeout
)

# Resource Usage Metrics
resource_usage = Gauge(
    "resource_usage",
    "Current resource usage",
    ["resource_type"],  # cpu_percent, memory_mb, disk_free_gb
)
