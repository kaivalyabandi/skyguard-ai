import pandas as pd

# ----------------------------------------
# STEP 1: READ THE ORIGINAL WEATHER DATA
# ----------------------------------------

data = pd.read_csv("weather_data.csv")

print("Original data loaded successfully.")
print("Total readings:", len(data))

# ----------------------------------------
# STEP 2: CREATE A COPY
# ----------------------------------------

faulty_data = data.copy()
faulty_data["injected_fault"] = "NONE"

# ----------------------------------------
# FAULT 1: TEMPERATURE SPIKE
# ----------------------------------------

spike_index = 10

if spike_index < len(faulty_data):

    original_value = faulty_data.loc[
        spike_index, "temperature"
    ]

    faulty_data.loc[
        spike_index, "temperature"
    ] = original_value + 25

    faulty_data.loc[
        spike_index, "injected_fault"
    ] = "TEMPERATURE_SPIKE"

# ----------------------------------------
# FAULT 2: TEMPERATURE DRIFT
# ----------------------------------------

start_index = 20
number_of_points = 6

if start_index + number_of_points <= len(faulty_data):

    for i in range(number_of_points):

        index = start_index + i

        faulty_data.loc[
            index, "temperature"
        ] += (i + 1) * 2

        faulty_data.loc[
            index, "injected_fault"
        ] = "TEMPERATURE_DRIFT"

# ----------------------------------------
# FAULT 3: TEMPERATURE FLATLINE
# ----------------------------------------

start_index = 35
number_of_points = 5

if start_index + number_of_points <= len(faulty_data):

    flat_value = faulty_data.loc[
        start_index, "temperature"
    ]

    for i in range(number_of_points):

        index = start_index + i

        faulty_data.loc[
            index, "temperature"
        ] = flat_value

        faulty_data.loc[
            index, "injected_fault"
        ] = "TEMPERATURE_FLATLINE"

# ----------------------------------------
# FAULT 4: HUMIDITY SPIKE
# ----------------------------------------

spike_index = 50

if spike_index < len(faulty_data):

    faulty_data.loc[
        spike_index, "humidity"
    ] = 99

    faulty_data.loc[
        spike_index, "injected_fault"
    ] = "HUMIDITY_SPIKE"

# ----------------------------------------
# FAULT 5: PRESSURE BIAS
# ----------------------------------------

start_index = 60
number_of_points = 5

if start_index + number_of_points <= len(faulty_data):

    for i in range(number_of_points):

        index = start_index + i

        faulty_data.loc[
            index, "pressure"
        ] += 15

        faulty_data.loc[
            index, "injected_fault"
        ] = "PRESSURE_BIAS"

# ----------------------------------------
# FAULT 6: SENSOR DROPOUT
# ----------------------------------------

start_index = 80
number_of_points = 3

if start_index + number_of_points <= len(faulty_data):

    for i in range(number_of_points):

        index = start_index + i

        # Simulate missing sensor readings
        faulty_data.loc[
            index, "temperature"
        ] = None

        faulty_data.loc[
            index, "humidity"
        ] = None

        faulty_data.loc[
            index, "pressure"
        ] = None

        faulty_data.loc[
            index, "injected_fault"
        ] = "SENSOR_DROPOUT"

# ----------------------------------------
# SAVE THE FAULTY DATA
# ----------------------------------------

faulty_data.to_csv(
    "weather_with_faults.csv",
    index=False
)

# ----------------------------------------
# DISPLAY RESULTS
# ----------------------------------------

print("\n----------------------------------------")
print("FAULT SIMULATION COMPLETE")
print("----------------------------------------")

fault_rows = faulty_data[
    faulty_data["injected_fault"] != "NONE"
]

print("\nInjected fault readings:")

print(
    fault_rows[
        [
            "temperature",
            "pressure",
            "humidity",
            "injected_fault"
        ]
    ]
)

print("\nNew file created:")
print("weather_with_faults.csv")