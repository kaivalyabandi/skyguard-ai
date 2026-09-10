import pandas as pd
from pathlib import Path

# ============================================================
# SKYGUARD AI
# CREATE FINAL SUPABASE OUTPUT
# ============================================================

print("========================================")
print("     SKYGUARD AI FINAL OUTPUT")
print("========================================")

project_folder = Path(__file__).resolve().parent

# ============================================================
# INPUT
# ============================================================

input_file = project_folder / "anomaly_results.csv"

if not input_file.exists():
    print()
    print("ERROR: anomaly_results.csv was not found.")
    print(input_file)
    raise SystemExit

data = pd.read_csv(input_file)

print("Input rows:", len(data))

# ============================================================
# REQUIRED SUPABASE COLUMNS
# ============================================================

required_columns = [
    "date",
    "temperature",
    "humidity",
    "pressure",
    "final_status",
    "fault_type",
    "confidence_percent",
    "confidence",
    "severity",
    "spatial_result",
    "temporal_result",
    "cross_sensor_result",
    "evidence_count",
    "reason",
    "recommendation"
]

missing_columns = [
    column
    for column in required_columns
    if column not in data.columns
]

if missing_columns:

    print()
    print("ERROR: Missing required columns:")
    
    for column in missing_columns:
        print("-", column)

    raise SystemExit

# ============================================================
# CREATE SUPABASE DATASET
# ============================================================

final_data = pd.DataFrame()

# ------------------------------------------------------------
# TIMESTAMP
# ------------------------------------------------------------

final_data["timestamp"] = pd.to_datetime(
    data["date"],
    errors="coerce"
)

# ------------------------------------------------------------
# STATION
# ------------------------------------------------------------

final_data["station_id"] = "STATION_A"

# ------------------------------------------------------------
# WEATHER VALUES
# ------------------------------------------------------------

final_data["temperature"] = pd.to_numeric(
    data["temperature"],
    errors="coerce"
)

final_data["humidity"] = pd.to_numeric(
    data["humidity"],
    errors="coerce"
)

final_data["pressure"] = pd.to_numeric(
    data["pressure"],
    errors="coerce"
)

# ------------------------------------------------------------
# DECISION ENGINE OUTPUT
# ------------------------------------------------------------

final_data["final_status"] = (
    data["final_status"]
)

final_data["fault_type"] = (
    data["fault_type"]
)

final_data["confidence_percent"] = pd.to_numeric(
    data["confidence_percent"],
    errors="coerce"
)

final_data["confidence"] = (
    data["confidence"]
)

final_data["severity"] = (
    data["severity"]
)

# ------------------------------------------------------------
# EVIDENCE
# ------------------------------------------------------------

final_data["spatial_result"] = (
    data["spatial_result"]
)

final_data["temporal_result"] = (
    data["temporal_result"]
)

final_data["cross_sensor_result"] = (
    data["cross_sensor_result"]
)

final_data["evidence_count"] = pd.to_numeric(
    data["evidence_count"],
    errors="coerce"
)

# ------------------------------------------------------------
# EXPLANATION
# ------------------------------------------------------------

final_data["reason"] = (
    data["reason"]
)

final_data["recommendation"] = (
    data["recommendation"]
)

# ============================================================
# CLEAN TIMESTAMP
# ============================================================

final_data["timestamp"] = (
    final_data["timestamp"]
    .dt.strftime("%Y-%m-%dT%H:%M:%S%z")
)

# ============================================================
# VALIDATION
# ============================================================

print()
print("========================================")
print("        FINAL OUTPUT VALIDATION")
print("========================================")

print(
    "Rows:",
    len(final_data)
)

print(
    "Columns:",
    len(final_data.columns)
)

print(
    "Station IDs:",
    final_data["station_id"]
    .unique()
    .tolist()
)

print()
print("Status breakdown:")

print(
    final_data["final_status"]
    .value_counts()
    .to_string()
)

print()
print("Fault breakdown:")

print(
    final_data["fault_type"]
    .value_counts()
    .to_string()
)

# ============================================================
# CHECK FUTURE DATES
# ============================================================

timestamps = pd.to_datetime(
    final_data["timestamp"],
    errors="coerce"
)

future_rows = (
    timestamps > pd.Timestamp.now(
        tz="Asia/Kolkata"
    )
).sum()

print()
print(
    "Future rows:",
    future_rows
)

if future_rows > 0:

    print()
    print(
        "WARNING: Future timestamps detected."
    )

# ============================================================
# CHECK NULLS
# ============================================================

print()
print("Null values:")

print(
    final_data.isna()
    .sum()
    .to_string()
)

# ============================================================
# OUTPUT FILE
# ============================================================

output_file = (
    project_folder /
    "skyguard_supabase_anomaly_results.csv"
)

final_data.to_csv(
    output_file,
    index=False
)

# ============================================================
# FINAL MESSAGE
# ============================================================

print()
print("========================================")
print("       FINAL FILE CREATED")
print("========================================")

print(
    "File:",
    output_file
)

print(
    "Rows:",
    len(final_data)
)

print(
    "Columns:",
    len(final_data.columns)
)

print()
print("Supabase-ready:")
print("YES")

print("========================================")