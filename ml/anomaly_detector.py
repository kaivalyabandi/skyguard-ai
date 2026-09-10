import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest

# ============================================================
# SKYGUARD AI - WEATHER ANOMALY DETECTOR
# ============================================================

print("========================================")
print("       WEATHER ANOMALY DETECTOR")
print("========================================")

# ============================================================
# STEP 1: PROJECT FOLDER
# ============================================================

project_folder = Path(__file__).resolve().parent

# ============================================================
# STEP 2: READ WEATHER DATA
# ============================================================

weather_file = project_folder / "weather_with_faults.csv"

if not weather_file.exists():
    print()
    print("ERROR: weather_with_faults.csv was not found.")
    print(weather_file)
    raise SystemExit

data = pd.read_csv(weather_file)

data["date"] = pd.to_datetime(data["date"])

data = (
    data
    .sort_values("date")
    .reset_index(drop=True)
)

print("Total weather readings :", len(data))

# ============================================================
# STEP 3: PREPARE FEATURES FOR ISOLATION FOREST
# ============================================================

features = [
    "temperature",
    "humidity",
    "pressure",
    "wind_speed",
    "precipitation"
]

ml_data = data[features].copy()

for column in features:
    ml_data[column] = (
        ml_data[column]
        .fillna(ml_data[column].median())
    )

# ============================================================
# STEP 4: ISOLATION FOREST
# ============================================================

model = IsolationForest(
    n_estimators=200,
    contamination=0.05,
    random_state=42
)

model.fit(ml_data)

data["isolation_prediction"] = model.predict(ml_data)

data["isolation_anomaly"] = (
    data["isolation_prediction"] == -1
)

data["isolation_score"] = (
    model.decision_function(ml_data)
)

# ============================================================
# STEP 5: TEMPORAL ANALYSIS
# ============================================================

data["temperature_change"] = (
    data["temperature"].diff()
)

data["humidity_change"] = (
    data["humidity"].diff()
)

data["pressure_change"] = (
    data["pressure"].diff()
)

# ============================================================
# TEMPERATURE SPIKE
# ============================================================

data["temperature_spike"] = (
    data["temperature_change"].abs() >= 5
)

# ============================================================
# TEMPERATURE FLATLINE
# ============================================================

data["temperature_flatline"] = (
    data["temperature"]
    .rolling(window=4)
    .apply(
        lambda x: len(set(x)) == 1,
        raw=False
    )
    .fillna(0)
    .astype(bool)
)

# ============================================================
# TEMPERATURE DRIFT
# ============================================================

data["temperature_drift"] = False

for i in range(3, len(data)):

    values = data.loc[
        i - 3:i,
        "temperature"
    ]

    differences = (
        values
        .diff()
        .dropna()
    )

    if (
        len(differences) == 3
        and (
            (differences > 0).all()
            or
            (differences < 0).all()
        )
        and differences.abs().sum() >= 6
    ):

        data.loc[
            i,
            "temperature_drift"
        ] = True

# ============================================================
# HUMIDITY SPIKE
# ============================================================

data["humidity_spike"] = (
    data["humidity_change"].abs() >= 10
)

# ============================================================
# PRESSURE CHANGE
# ============================================================

data["pressure_change_flag"] = (
    data["pressure_change"].abs() >= 8
)

# ============================================================
# STEP 6: SENSOR DROPOUT
# ============================================================

data["sensor_dropout"] = (
    data[
        [
            "temperature",
            "humidity",
            "pressure"
        ]
    ]
    .isna()
    .any(axis=1)
)

# ============================================================
# STEP 7: CROSS-SENSOR CONSISTENCY
# ============================================================

temperature_inconsistency = (
    (data["temperature_change"].abs() >= 5)
    &
    (data["humidity_change"].abs() <= 3)
    &
    (data["pressure_change"].abs() <= 3)
)

humidity_inconsistency = (
    (data["humidity_change"].abs() >= 10)
    &
    (data["temperature_change"].abs() <= 3)
    &
    (data["pressure_change"].abs() <= 3)
)

pressure_inconsistency = (
    (data["pressure_change"].abs() >= 8)
    &
    (data["temperature_change"].abs() <= 3)
    &
    (data["humidity_change"].abs() <= 5)
)

data["cross_sensor_inconsistency"] = (
    temperature_inconsistency
    |
    humidity_inconsistency
    |
    pressure_inconsistency
)

data["cross_sensor_result"] = "NORMAL"

for i in range(len(data)):

    results = []

    if temperature_inconsistency.iloc[i]:
        results.append("TEMPERATURE_INCONSISTENCY")

    if humidity_inconsistency.iloc[i]:
        results.append("HUMIDITY_INCONSISTENCY")

    if pressure_inconsistency.iloc[i]:
        results.append("PRESSURE_INCONSISTENCY")

    if results:
        data.loc[i, "cross_sensor_result"] = (
            "; ".join(results)
        )

data["cross_sensor_reason"] = (
    data["cross_sensor_result"]
)

# ============================================================
# STEP 8: 3-STATION SPATIAL COMPARISON
# ============================================================

station_b_file = (
    project_folder /
    "reference_station_data.csv"
)

station_c_file = (
    project_folder /
    "comparison_station_data.csv"
)

station_b = pd.read_csv(station_b_file)
station_c = pd.read_csv(station_c_file)

station_b["date"] = pd.to_datetime(
    station_b["date"]
)

station_c["date"] = pd.to_datetime(
    station_c["date"]
)

# ------------------------------------------------------------
# STATION B
# ------------------------------------------------------------

station_b = station_b.rename(
    columns={
        "temperature": "station_b_temperature",
        "humidity": "station_b_humidity",
        "pressure": "station_b_pressure"
    }
)

station_b = station_b[
    [
        "date",
        "station_b_temperature",
        "station_b_humidity",
        "station_b_pressure"
    ]
]

# ------------------------------------------------------------
# STATION C
# ------------------------------------------------------------

station_c = station_c.rename(
    columns={
        "temperature": "station_c_temperature",
        "humidity": "station_c_humidity",
        "pressure": "station_c_pressure"
    }
)

station_c = station_c[
    [
        "date",
        "station_c_temperature",
        "station_c_humidity",
        "station_c_pressure"
    ]
]

# ------------------------------------------------------------
# MERGE
# ------------------------------------------------------------

data = data.merge(
    station_b,
    on="date",
    how="left"
)

data = data.merge(
    station_c,
    on="date",
    how="left"
)

# ------------------------------------------------------------
# PRIMARY vs STATION B
# ------------------------------------------------------------

data["temperature_difference_b"] = (
    data["temperature"]
    -
    data["station_b_temperature"]
).abs()

data["humidity_difference_b"] = (
    data["humidity"]
    -
    data["station_b_humidity"]
).abs()

data["pressure_difference_b"] = (
    data["pressure"]
    -
    data["station_b_pressure"]
).abs()

# ------------------------------------------------------------
# PRIMARY vs STATION C
# ------------------------------------------------------------

data["temperature_difference_c"] = (
    data["temperature"]
    -
    data["station_c_temperature"]
).abs()

data["humidity_difference_c"] = (
    data["humidity"]
    -
    data["station_c_humidity"]
).abs()

data["pressure_difference_c"] = (
    data["pressure"]
    -
    data["station_c_pressure"]
).abs()

# ------------------------------------------------------------
# STATION B FLAGS
# ------------------------------------------------------------

spatial_temperature_flag_b = (
    data["temperature_difference_b"] >= 5
)

spatial_humidity_flag_b = (
    data["humidity_difference_b"] >= 10
)

spatial_pressure_flag_b = (
    data["pressure_difference_b"] >= 8
)

station_b_inconsistent = (
    spatial_temperature_flag_b
    |
    spatial_humidity_flag_b
    |
    spatial_pressure_flag_b
)

# ------------------------------------------------------------
# STATION C FLAGS
# ------------------------------------------------------------

spatial_temperature_flag_c = (
    data["temperature_difference_c"] >= 5
)

spatial_humidity_flag_c = (
    data["humidity_difference_c"] >= 10
)

spatial_pressure_flag_c = (
    data["pressure_difference_c"] >= 8
)

station_c_inconsistent = (
    spatial_temperature_flag_c
    |
    spatial_humidity_flag_c
    |
    spatial_pressure_flag_c
)

# ------------------------------------------------------------
# PRIMARY POSSIBLE OUTLIER
# ------------------------------------------------------------

data["spatial_inconsistency"] = (
    station_b_inconsistent
    &
    station_c_inconsistent
)

# ------------------------------------------------------------
# SPATIAL RESULT
# ------------------------------------------------------------

data["spatial_result"] = "NORMAL"

data.loc[
    station_b_inconsistent
    &
    ~station_c_inconsistent,
    "spatial_result"
] = "STATION B CHECK"

data.loc[
    ~station_b_inconsistent
    &
    station_c_inconsistent,
    "spatial_result"
] = "STATION C CHECK"

data.loc[
    station_b_inconsistent
    &
    station_c_inconsistent,
    "spatial_result"
] = "PRIMARY POSSIBLE OUTLIER"

# ------------------------------------------------------------
# SPATIAL REASON
# ------------------------------------------------------------

data["spatial_reason"] = "NORMAL"

for i in range(len(data)):

    results = []

    if spatial_temperature_flag_b.iloc[i]:
        results.append(
            "STATION B TEMPERATURE DIFFERENCE"
        )

    if spatial_humidity_flag_b.iloc[i]:
        results.append(
            "STATION B HUMIDITY DIFFERENCE"
        )

    if spatial_pressure_flag_b.iloc[i]:
        results.append(
            "STATION B PRESSURE DIFFERENCE"
        )

    if spatial_temperature_flag_c.iloc[i]:
        results.append(
            "STATION C TEMPERATURE DIFFERENCE"
        )

    if spatial_humidity_flag_c.iloc[i]:
        results.append(
            "STATION C HUMIDITY DIFFERENCE"
        )

    if spatial_pressure_flag_c.iloc[i]:
        results.append(
            "STATION C PRESSURE DIFFERENCE"
        )

    if results:
        data.loc[i, "spatial_reason"] = (
            "; ".join(results)
        )

# ------------------------------------------------------------
# COMPATIBILITY COLUMNS
# ------------------------------------------------------------

data["temperature_difference"] = data[
    [
        "temperature_difference_b",
        "temperature_difference_c"
    ]
].max(axis=1)

data["humidity_difference"] = data[
    [
        "humidity_difference_b",
        "humidity_difference_c"
    ]
].max(axis=1)

data["pressure_difference"] = data[
    [
        "pressure_difference_b",
        "pressure_difference_c"
    ]
].max(axis=1)

# ============================================================
# STEP 9: TEMPORAL BREAKDOWN
# ============================================================

data["temporal_evidence"] = (
    data["temperature_spike"]
    |
    data["temperature_flatline"]
    |
    data["temperature_drift"]
    |
    data["humidity_spike"]
    |
    data["pressure_change_flag"]
)

data["temporal_result"] = "NORMAL"

for i in range(len(data)):

    results = []

    if data.loc[i, "temperature_spike"]:
        results.append("TEMPERATURE_SPIKE")

    if data.loc[i, "temperature_flatline"]:
        results.append("TEMPERATURE_FLATLINE")

    if data.loc[i, "temperature_drift"]:
        results.append("TEMPERATURE_DRIFT")

    if data.loc[i, "humidity_spike"]:
        results.append("HUMIDITY_SPIKE")

    if data.loc[i, "pressure_change_flag"]:
        results.append("PRESSURE_CHANGE")

    if results:
        data.loc[i, "temporal_result"] = (
            "; ".join(results)
        )

# ============================================================
# STEP 10: EVIDENCE COUNT
# ============================================================

data["evidence_count"] = (
    data["isolation_anomaly"].astype(int)
    +
    data["temporal_evidence"].astype(int)
    +
    data["cross_sensor_inconsistency"].astype(int)
    +
    data["spatial_inconsistency"].astype(int)
    +
    data["sensor_dropout"].astype(int)
)

# ============================================================
# STEP 11: DECISION ENGINE
# ============================================================
#
# IMPORTANT DESIGN RULE:
#
# Spatial disagreement alone does NOT automatically mean
# SENSOR FAULT.
#
# Spatial evidence is treated as supporting evidence.
#
# Direct sensor evidence:
#   dropout / spike / drift / flatline / humidity spike /
#   pressure change / cross-sensor inconsistency
#   -> SENSOR FAULT
#
# Spatial + independent evidence:
#   spatial + ML
#   spatial + temporal
#   spatial + cross-sensor
#   -> SENSOR FAULT
#
# Spatial only:
#   -> POSSIBLE ANOMALY
#
# This reduces false sensor-fault declarations caused only
# by local weather differences.

data["final_status"] = "NORMAL"

direct_fault_condition = (
    data["sensor_dropout"]
    |
    data["temperature_spike"]
    |
    data["temperature_drift"]
    |
    data["temperature_flatline"]
    |
    data["humidity_spike"]
    |
    data["pressure_change_flag"]
    |
    data["cross_sensor_inconsistency"]
)

spatial_supported_fault = (
    data["spatial_inconsistency"]
    &
    (
        data["isolation_anomaly"]
        |
        data["temporal_evidence"]
        |
        data["cross_sensor_inconsistency"]
    )
)

sensor_fault_condition = (
    direct_fault_condition
    |
    spatial_supported_fault
)

data.loc[
    sensor_fault_condition,
    "final_status"
] = "SENSOR FAULT"

# ------------------------------------------------------------
# POSSIBLE ANOMALY
# ------------------------------------------------------------

possible_anomaly_condition = (
    (data["final_status"] == "NORMAL")
    &
    (
        data["isolation_anomaly"]
        |
        data["spatial_inconsistency"]
    )
)

data.loc[
    possible_anomaly_condition,
    "final_status"
] = "POSSIBLE ANOMALY"

# ============================================================
# STEP 12: FAULT CLASSIFICATION
# ============================================================

data["fault_type"] = "NONE"

# ------------------------------------------------------------
# DROPOUT
# ------------------------------------------------------------

data.loc[
    data["sensor_dropout"],
    "fault_type"
] = "SENSOR DROPOUT"

# ------------------------------------------------------------
# TEMPERATURE SPIKE
# ------------------------------------------------------------

data.loc[
    (data["fault_type"] == "NONE")
    &
    data["temperature_spike"],
    "fault_type"
] = "TEMPERATURE SPIKE"

# ------------------------------------------------------------
# TEMPERATURE FLATLINE
# ------------------------------------------------------------

data.loc[
    (data["fault_type"] == "NONE")
    &
    data["temperature_flatline"],
    "fault_type"
] = "TEMPERATURE FLATLINE"

# ------------------------------------------------------------
# TEMPERATURE DRIFT
# ------------------------------------------------------------

data.loc[
    (data["fault_type"] == "NONE")
    &
    data["temperature_drift"],
    "fault_type"
] = "TEMPERATURE DRIFT"

# ------------------------------------------------------------
# HUMIDITY SPIKE
# ------------------------------------------------------------

data.loc[
    (data["fault_type"] == "NONE")
    &
    data["humidity_spike"],
    "fault_type"
] = "HUMIDITY SPIKE"

# ------------------------------------------------------------
# PRESSURE TEMPORAL CHANGE
# ------------------------------------------------------------

data.loc[
    (data["fault_type"] == "NONE")
    &
    data["pressure_change_flag"],
    "fault_type"
] = "PRESSURE ANOMALY"

# ------------------------------------------------------------
# PRESSURE SPATIAL BIAS
# ------------------------------------------------------------

data.loc[
    (data["fault_type"] == "NONE")
    &
    data["spatial_reason"].str.contains(
        "PRESSURE DIFFERENCE",
        na=False
    ),
    "fault_type"
] = "PRESSURE SENSOR BIAS"

# ------------------------------------------------------------
# CROSS-SENSOR HUMIDITY
# ------------------------------------------------------------

data.loc[
    (data["fault_type"] == "NONE")
    &
    data["cross_sensor_result"].str.contains(
        "HUMIDITY_INCONSISTENCY",
        na=False
    ),
    "fault_type"
] = "HUMIDITY ANOMALY"

# ------------------------------------------------------------
# CROSS-SENSOR PRESSURE
# ------------------------------------------------------------

data.loc[
    (data["fault_type"] == "NONE")
    &
    data["cross_sensor_result"].str.contains(
        "PRESSURE_INCONSISTENCY",
        na=False
    ),
    "fault_type"
] = "PRESSURE ANOMALY"

# ------------------------------------------------------------
# TEMPERATURE SPATIAL BIAS
# ------------------------------------------------------------

data.loc[
    (data["fault_type"] == "NONE")
    &
    data["spatial_reason"].str.contains(
        "TEMPERATURE DIFFERENCE",
        na=False
    ),
    "fault_type"
] = "TEMPERATURE SENSOR BIAS"

# ------------------------------------------------------------
# HUMIDITY SPATIAL BIAS
# ------------------------------------------------------------

data.loc[
    (data["fault_type"] == "NONE")
    &
    data["spatial_reason"].str.contains(
        "HUMIDITY DIFFERENCE",
        na=False
    ),
    "fault_type"
] = "HUMIDITY SENSOR BIAS"

# ------------------------------------------------------------
# ISOLATION FOREST ONLY
# ------------------------------------------------------------

data.loc[
    (data["fault_type"] == "NONE")
    &
    data["isolation_anomaly"],
    "fault_type"
] = "MULTIVARIATE ANOMALY"

# ------------------------------------------------------------
# SAFETY NET
# ------------------------------------------------------------

data.loc[
    (data["final_status"] == "SENSOR FAULT")
    &
    (data["fault_type"] == "NONE"),
    "fault_type"
] = "SENSOR ANOMALY"

# ============================================================
# STEP 13: CONFIDENCE SCORE
# ============================================================

data["confidence_score"] = (
    data["isolation_anomaly"].astype(int)
    +
    data["temporal_evidence"].astype(int)
    +
    data["cross_sensor_inconsistency"].astype(int)
    +
    data["spatial_inconsistency"].astype(int)
)

data["confidence_percent"] = (
    data["confidence_score"]
    / 4
    * 100
)

# Dropout is definitive missing-data evidence.
data.loc[
    data["sensor_dropout"],
    "confidence_percent"
] = 100

# Direct temporal evidence gets at least MEDIUM confidence.
direct_fault = (
    data["temperature_spike"]
    |
    data["temperature_drift"]
    |
    data["temperature_flatline"]
    |
    data["humidity_spike"]
    |
    data["pressure_change_flag"]
)

data.loc[
    direct_fault
    &
    (data["confidence_percent"] < 50),
    "confidence_percent"
] = 50

# Spatial-only evidence should remain LOW confidence.
spatial_only = (
    data["spatial_inconsistency"]
    &
    ~direct_fault
    &
    ~data["cross_sensor_inconsistency"]
    &
    ~data["isolation_anomaly"]
)

data.loc[
    spatial_only,
    "confidence_percent"
] = 25

# ------------------------------------------------------------
# CONFIDENCE LEVEL
# ------------------------------------------------------------

data["confidence"] = "LOW"

data.loc[
    data["confidence_percent"] >= 50,
    "confidence"
] = "MEDIUM"

data.loc[
    data["confidence_percent"] >= 75,
    "confidence"
] = "HIGH"

data.loc[
    data["sensor_dropout"],
    "confidence"
] = "HIGH"

# ============================================================
# STEP 14: SEVERITY
# ============================================================

data["severity"] = "NORMAL"

data.loc[
    data["final_status"] == "POSSIBLE ANOMALY",
    "severity"
] = "LOW"

data.loc[
    (data["final_status"] == "SENSOR FAULT")
    &
    (data["confidence_percent"] < 75),
    "severity"
] = "MEDIUM"

data.loc[
    (data["final_status"] == "SENSOR FAULT")
    &
    (data["confidence_percent"] >= 75),
    "severity"
] = "HIGH"

critical_condition = (
    data["sensor_dropout"]
    |
    (data["temperature_difference"] >= 15)
    |
    (data["pressure_difference"] >= 15)
    |
    (data["temperature_change"].abs() >= 15)
)

data.loc[
    critical_condition
    &
    (data["final_status"] == "SENSOR FAULT"),
    "severity"
] = "CRITICAL"

# ============================================================
# STEP 15: EXPLANATION
# ============================================================

data["reason"] = (
    "All monitoring checks normal."
)

for i in range(len(data)):

    reasons = []

    if data.loc[i, "isolation_anomaly"]:
        reasons.append(
            "Isolation Forest anomaly"
        )

    if data.loc[i, "temperature_spike"]:
        reasons.append(
            "sudden temperature change"
        )

    if data.loc[i, "temperature_flatline"]:
        reasons.append(
            "temperature value stuck"
        )

    if data.loc[i, "temperature_drift"]:
        reasons.append(
            "gradual temperature drift"
        )

    if data.loc[i, "humidity_spike"]:
        reasons.append(
            "sudden humidity change"
        )

    if data.loc[i, "pressure_change_flag"]:
        reasons.append(
            "sudden pressure change"
        )

    if data.loc[i, "sensor_dropout"]:
        reasons.append(
            "sensor data missing"
        )

    if data.loc[i, "cross_sensor_inconsistency"]:
        reasons.append(
            data.loc[i, "cross_sensor_result"]
        )

    if data.loc[i, "spatial_inconsistency"]:
        reasons.append(
            data.loc[i, "spatial_result"]
        )
    elif data.loc[i, "spatial_result"] != "NORMAL":
        reasons.append(
            data.loc[i, "spatial_result"]
        )

    if len(reasons) > 0:
        data.loc[i, "reason"] = (
            "; ".join(reasons)
        )

# ============================================================
# STEP 16: RECOMMENDATION
# ============================================================

data["recommendation"] = (
    "Continue normal monitoring."
)

data.loc[
    data["fault_type"] == "SENSOR DROPOUT",
    "recommendation"
] = (
    "Check sensor power, communication "
    "link, and connection."
)

data.loc[
    data["fault_type"] == "TEMPERATURE SPIKE",
    "recommendation"
] = (
    "Inspect temperature sensor and "
    "verify calibration."
)

data.loc[
    data["fault_type"] == "TEMPERATURE FLATLINE",
    "recommendation"
] = (
    "Check for a stuck or frozen "
    "temperature sensor."
)

data.loc[
    data["fault_type"] == "TEMPERATURE DRIFT",
    "recommendation"
] = (
    "Inspect temperature sensor for "
    "calibration drift."
)

data.loc[
    data["fault_type"] == "HUMIDITY SPIKE",
    "recommendation"
] = (
    "Inspect humidity sensor and "
    "verify calibration."
)

data.loc[
    data["fault_type"] == "HUMIDITY ANOMALY",
    "recommendation"
] = (
    "Inspect humidity sensor and "
    "verify calibration."
)

data.loc[
    data["fault_type"] == "PRESSURE ANOMALY",
    "recommendation"
] = (
    "Inspect pressure sensor and "
    "verify calibration."
)

data.loc[
    data["fault_type"] == "TEMPERATURE SENSOR BIAS",
    "recommendation"
] = (
    "Compare temperature sensor with "
    "nearby stations and recalibrate "
    "if required."
)

data.loc[
    data["fault_type"] == "HUMIDITY SENSOR BIAS",
    "recommendation"
] = (
    "Compare humidity sensor with "
    "nearby stations and recalibrate "
    "if required."
)

data.loc[
    data["fault_type"] == "PRESSURE SENSOR BIAS",
    "recommendation"
] = (
    "Compare pressure sensor with "
    "nearby stations and recalibrate "
    "if required."
)

data.loc[
    data["fault_type"] == "MULTIVARIATE ANOMALY",
    "recommendation"
] = (
    "Investigate sensor readings and "
    "verify station health."
)

data.loc[
    data["fault_type"] == "SENSOR ANOMALY",
    "recommendation"
] = (
    "Inspect the affected sensor and "
    "verify station health."
)

# ============================================================
# STEP 17: 3-STATION SPATIAL SUMMARY
# ============================================================

print("\n========================================")
print("       3-STATION SPATIAL SUMMARY")
print("========================================")

print(
    "Normal spatial readings:",
    (data["spatial_result"] == "NORMAL").sum()
)

print(
    "Station B checks:",
    (data["spatial_result"] == "STATION B CHECK").sum()
)

print(
    "Station C checks:",
    (data["spatial_result"] == "STATION C CHECK").sum()
)

print(
    "Primary possible outliers:",
    (data["spatial_result"] == "PRIMARY POSSIBLE OUTLIER").sum()
)

# ============================================================
# STEP 18: BREAKDOWN FIELD CHECK
# ============================================================

print("\n========================================")
print("       BREAKDOWN FIELD CHECK")
print("========================================")

print(
    "Total rows:",
    len(data)
)

print(
    "Temporal result filled:",
    data["temporal_result"].notna().sum(),
    "/",
    len(data)
)

print(
    "Spatial result filled:",
    data["spatial_result"].notna().sum(),
    "/",
    len(data)
)

print(
    "Cross-sensor result filled:",
    data["cross_sensor_result"].notna().sum(),
    "/",
    len(data)
)

print(
    "Evidence count filled:",
    data["evidence_count"].notna().sum(),
    "/",
    len(data)
)

# ============================================================
# STEP 19: FINAL SUMMARY
# ============================================================

print("\n========================================")
print("       DECISION ENGINE SUMMARY")
print("========================================")

print(
    "Normal readings       :",
    (
        data["final_status"] == "NORMAL"
    ).sum()
)

print(
    "Possible anomalies    :",
    (
        data["final_status"] == "POSSIBLE ANOMALY"
    ).sum()
)

print(
    "Sensor faults         :",
    (
        data["final_status"] == "SENSOR FAULT"
    ).sum()
)

print(
    "High confidence faults:",
    (
        (data["final_status"] == "SENSOR FAULT")
        &
        (data["confidence"] == "HIGH")
    ).sum()
)

# ============================================================
# STEP 20: DISPLAY FINAL DECISIONS
# ============================================================

final_results = data[
    data["final_status"] != "NORMAL"
]

print("\n========================================")
print("       FINAL DECISION RESULTS")
print("========================================")

for _, row in final_results.iterrows():

    print("\nTime:", row["date"])

    print(
        "Temperature:",
        round(row["temperature"], 2)
        if pd.notna(row["temperature"])
        else "MISSING",
        "°C"
    )

    print(
        "Humidity:",
        round(row["humidity"], 2)
        if pd.notna(row["humidity"])
        else "MISSING",
        "%"
    )

    print(
        "Pressure:",
        round(row["pressure"], 2)
        if pd.notna(row["pressure"])
        else "MISSING",
        "hPa"
    )

    print(
        "FINAL STATUS:",
        row["final_status"]
    )

    print(
        "FAULT TYPE:",
        row["fault_type"]
    )

    print(
        "TEMPORAL RESULT:",
        row["temporal_result"]
    )

    print(
        "SPATIAL RESULT:",
        row["spatial_result"]
    )

    print(
        "CROSS-SENSOR RESULT:",
        row["cross_sensor_result"]
    )

    print(
        "CONFIDENCE:",
        row["confidence"],
        f"({row['confidence_percent']:.0f}%)"
    )

    print(
        "SEVERITY:",
        row["severity"]
    )

    print(
        "EVIDENCE COUNT:",
        row["evidence_count"]
    )

    print(
        "REASON:",
        row["reason"]
    )

    print(
        "RECOMMENDATION:",
        row["recommendation"]
    )

# ============================================================
# STEP 21: SAVE COMPLETE RESULTS
# ============================================================

output_file = (
    project_folder /
    "anomaly_results.csv"
)

data.to_csv(
    output_file,
    index=False
)

print("\n========================================")
print("Results saved to:")
print(output_file)
print("========================================")