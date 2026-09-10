import pandas as pd
from pathlib import Path

# -------------------------------------------------------
# FILE PATH
# -------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

primary_file = BASE_DIR / "weather_data.csv"
station_b_file = BASE_DIR / "reference_station_data.csv"
station_c_file = BASE_DIR / "comparison_station_data.csv"

output_file = BASE_DIR / "three_station_comparison.csv"


# -------------------------------------------------------
# READ DATA
# -------------------------------------------------------

primary = pd.read_csv(primary_file)
station_b = pd.read_csv(station_b_file)
station_c = pd.read_csv(station_c_file)

# Convert timestamps
primary["date"] = pd.to_datetime(primary["date"])
station_b["date"] = pd.to_datetime(station_b["date"])
station_c["date"] = pd.to_datetime(station_c["date"])


# -------------------------------------------------------
# SELECT REQUIRED COLUMNS
# -------------------------------------------------------

primary = primary[
    ["date", "temperature", "humidity", "pressure"]
].rename(columns={
    "temperature": "primary_temperature",
    "humidity": "primary_humidity",
    "pressure": "primary_pressure"
})

station_b = station_b[
    ["date", "temperature", "humidity", "pressure"]
].rename(columns={
    "temperature": "station_b_temperature",
    "humidity": "station_b_humidity",
    "pressure": "station_b_pressure"
})

station_c = station_c[
    ["date", "temperature", "humidity", "pressure"]
].rename(columns={
    "temperature": "station_c_temperature",
    "humidity": "station_c_humidity",
    "pressure": "station_c_pressure"
})


# -------------------------------------------------------
# MERGE ALL THREE STATIONS
# -------------------------------------------------------

comparison = primary.merge(
    station_b,
    on="date",
    how="inner"
)

comparison = comparison.merge(
    station_c,
    on="date",
    how="inner"
)


# -------------------------------------------------------
# CALCULATE DIFFERENCES
# -------------------------------------------------------

# Primary vs Station B
comparison["temp_difference_b"] = (
    comparison["primary_temperature"]
    - comparison["station_b_temperature"]
).abs()

comparison["humidity_difference_b"] = (
    comparison["primary_humidity"]
    - comparison["station_b_humidity"]
).abs()

comparison["pressure_difference_b"] = (
    comparison["primary_pressure"]
    - comparison["station_b_pressure"]
).abs()


# Primary vs Station C
comparison["temp_difference_c"] = (
    comparison["primary_temperature"]
    - comparison["station_c_temperature"]
).abs()

comparison["humidity_difference_c"] = (
    comparison["primary_humidity"]
    - comparison["station_c_humidity"]
).abs()

comparison["pressure_difference_c"] = (
    comparison["primary_pressure"]
    - comparison["station_c_pressure"]
).abs()


# -------------------------------------------------------
# CHECK SPATIAL CONSISTENCY
# -------------------------------------------------------

comparison["station_b_status"] = "NORMAL"

comparison.loc[
    (comparison["temp_difference_b"] >= 5) |
    (comparison["humidity_difference_b"] >= 10) |
    (comparison["pressure_difference_b"] >= 8),
    "station_b_status"
] = "INCONSISTENT"


comparison["station_c_status"] = "NORMAL"

comparison.loc[
    (comparison["temp_difference_c"] >= 5) |
    (comparison["humidity_difference_c"] >= 10) |
    (comparison["pressure_difference_c"] >= 8),
    "station_c_status"
] = "INCONSISTENT"


# -------------------------------------------------------
# OVERALL SPATIAL STATUS
# -------------------------------------------------------

comparison["spatial_status"] = "NORMAL"

comparison.loc[
    (comparison["station_b_status"] == "INCONSISTENT") |
    (comparison["station_c_status"] == "INCONSISTENT"),
    "spatial_status"
] = "CHECK"


# If BOTH comparison stations disagree with Primary,
# mark it as a stronger spatial inconsistency.

comparison.loc[
    (comparison["station_b_status"] == "INCONSISTENT") &
    (comparison["station_c_status"] == "INCONSISTENT"),
    "spatial_status"
] = "PRIMARY POSSIBLE OUTLIER"


# -------------------------------------------------------
# SAVE FILE
# -------------------------------------------------------

comparison.to_csv(output_file, index=False)


# -------------------------------------------------------
# PRINT RESULTS
# -------------------------------------------------------

print()
print("=" * 60)
print("        THREE-STATION SPATIAL COMPARISON")
print("=" * 60)

print()
print("Primary station readings:", len(primary))
print("Station B readings:", len(station_b))
print("Station C readings:", len(station_c))
print("Compared readings:", len(comparison))

print()
print("-------------------------------------------------------")
print("SPATIAL STATUS")
print("-------------------------------------------------------")

print(comparison["spatial_status"].value_counts())

print()
print("-------------------------------------------------------")
print("STATION B STATUS")
print("-------------------------------------------------------")

print(comparison["station_b_status"].value_counts())

print()
print("-------------------------------------------------------")
print("STATION C STATUS")
print("-------------------------------------------------------")

print(comparison["station_c_status"].value_counts())

print()
print("-------------------------------------------------------")
print("SAMPLE COMPARISON")
print("-------------------------------------------------------")

print(
    comparison[
        [
            "date",
            "primary_temperature",
            "station_b_temperature",
            "station_c_temperature",
            "temp_difference_b",
            "temp_difference_c",
            "spatial_status"
        ]
    ].head(10)
)

print()
print("=" * 60)
print("FILE CREATED")
print("=" * 60)

print(output_file)

print()
print("THREE-STATION COMPARISON COMPLETED")