
import pandas as pd
from pathlib import Path

# ============================================================
# SKYGUARD AI - DETECTOR VALIDATION
# ============================================================

print("========================================")
print("       SKYGUARD AI VALIDATION")
print("========================================")

# Find project folder
project_folder = Path(__file__).resolve().parent

# ============================================================
# STEP 1: READ THE TWO FILES
# ============================================================

fault_data_file = project_folder / "weather_with_faults.csv"
result_file = project_folder / "anomaly_results.csv"

fault_data = pd.read_csv(fault_data_file)
results = pd.read_csv(result_file)

print("\nInput files loaded successfully.")
print("Total readings:", len(fault_data))

# ============================================================
# STEP 2: DEFINE THE FAULTS WE INTENTIONALLY INJECTED
# ============================================================

expected_faults = [
    "TEMPERATURE_SPIKE",
    "TEMPERATURE_DRIFT",
    "TEMPERATURE_FLATLINE",
    "HUMIDITY_SPIKE",
    "PRESSURE_BIAS",
    "SENSOR_DROPOUT"
]

# ============================================================
# STEP 3: CHECK EACH INJECTED FAULT
# ============================================================

print("\n========================================")
print("       FAULT DETECTION CHECK")
print("========================================")

validation_results = []

for fault in expected_faults:

    # Rows where this fault was intentionally injected
    injected_rows = fault_data[
        fault_data["injected_fault"] == fault
    ]

    # Their timestamps
    fault_times = injected_rows["date"].astype(str)

    # Find corresponding rows in detector results
    detected_rows = results[
        results["date"].astype(str).isin(fault_times)
    ]

    # A fault is considered detected if at least
    # one corresponding reading was marked abnormal
    abnormal_rows = detected_rows[
        detected_rows["final_status"] != "NORMAL"
    ]

    detected = len(abnormal_rows) > 0

    if detected:
        status = "DETECTED"
    else:
        status = "MISSED"

    validation_results.append(
        {
            "Expected Fault": fault,
            "Injected Readings": len(injected_rows),
            "Abnormal Readings Detected": len(abnormal_rows),
            "Status": status
        }
    )

    print("\nFault:", fault)
    print("Injected readings:", len(injected_rows))
    print(
        "Abnormal readings detected:",
        len(abnormal_rows)
    )
    print("Result:", status)

# ============================================================
# STEP 4: DISPLAY VALIDATION TABLE
# ============================================================

validation_table = pd.DataFrame(
    validation_results
)

print("\n========================================")
print("       VALIDATION SUMMARY")
print("========================================")

print(
    validation_table.to_string(index=False)
)

# ============================================================
# STEP 5: OVERALL DETECTION RATE
# ============================================================

detected_count = (
    validation_table["Status"]
    == "DETECTED"
).sum()

total_fault_types = len(expected_faults)

detection_rate = (
    detected_count / total_fault_types
) * 100

print("\n========================================")
print("       OVERALL PERFORMANCE")
print("========================================")

print(
    "Fault types tested :",
    total_fault_types
)

print(
    "Fault types detected:",
    detected_count
)

print(
    "Fault types missed  :",
    total_fault_types - detected_count
)

print(
    f"Detection rate      : {detection_rate:.1f}%"
)

# ============================================================
# STEP 6: SAVE VALIDATION REPORT
# ============================================================

validation_file = (
    project_folder /
    "validation_report.csv"
)

validation_table.to_csv(
    validation_file,
    index=False
)

print("\nValidation report saved to:")
print(validation_file)

print("\n========================================")
print("       VALIDATION COMPLETE")
print("========================================")

