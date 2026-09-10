
import openmeteo_requests
import pandas as pd
from pathlib import Path
from datetime import datetime


# ============================================================
# SKYGUARD AI - THREE LOCATION WEATHER DATA
# CURRENT + PAST OBSERVATIONS ONLY
# ============================================================

print("=" * 60)
print("        SKYGUARD AI WEATHER DATA")
print("        CURRENT + HISTORICAL DATA")
print("=" * 60)


# ------------------------------------------------------------
# PROJECT FOLDER
# ------------------------------------------------------------

project_folder = Path(__file__).resolve().parent


# ------------------------------------------------------------
# THREE LOCATIONS
# ------------------------------------------------------------

# MAIN / PRIMARY LOCATION
primary_latitude = 17.6868
primary_longitude = 83.2185

# COMPARISON LOCATION 1
reference_latitude = 17.6913
reference_longitude = 83.0039

# COMPARISON LOCATION 2
comparison_latitude = 17.7000
comparison_longitude = 83.1000


# ------------------------------------------------------------
# DATA WINDOW
# ------------------------------------------------------------
#
# IMPORTANT:
# We do NOT want future forecast values in the SkyGuard
# anomaly-detection dataset.
#
# We request recent past hourly data and then keep only
# timestamps that are <= the current India time.
#
# This gives us:
#
#       PAST DATA
#           +
#       CURRENT DATA
#           ↓
#       ANOMALY DETECTION
#
# Instead of:
#
#       PAST + FUTURE FORECAST
#
# ------------------------------------------------------------

PAST_HOURS = 168


# ------------------------------------------------------------
# OPEN-METEO API
# ------------------------------------------------------------

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": [
        primary_latitude,
        reference_latitude,
        comparison_latitude
    ],

    "longitude": [
        primary_longitude,
        reference_longitude,
        comparison_longitude
    ],

    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "surface_pressure",
        "wind_speed_10m",
        "precipitation",
        "rain"
    ],

    # Return recent historical/past hourly values.
    "past_hours": PAST_HOURS,

    # Do not intentionally request a future forecast window.
    "forecast_hours": 0,

    # Return timestamps in Indian Standard Time.
    "timezone": "Asia/Kolkata"
}


# ------------------------------------------------------------
# CURRENT INDIA TIME
# ------------------------------------------------------------

now_india = pd.Timestamp.now(tz="Asia/Kolkata")

print()
print("Current India time:")
print(now_india)


# ------------------------------------------------------------
# REQUEST WEATHER DATA
# ------------------------------------------------------------

try:

    openmeteo = openmeteo_requests.Client()

    responses = openmeteo.weather_api(
        url,
        params=params
    )

except Exception as e:

    print()
    print("ERROR: Could not retrieve weather data.")
    print(e)

    raise SystemExit


print()
print("Weather data received successfully.")


# ------------------------------------------------------------
# PROCESS ONE LOCATION
# ------------------------------------------------------------

def process_station(
    response,
    station_id,
    station_name
):

    hourly = response.Hourly()

    # --------------------------------------------------------
    # CREATE TIMESTAMP SERIES
    # --------------------------------------------------------

    time = pd.date_range(
        start=pd.to_datetime(
            hourly.Time(),
            unit="s",
            utc=True
        ),
        end=pd.to_datetime(
            hourly.TimeEnd(),
            unit="s",
            utc=True
        ),
        freq=pd.Timedelta(
            seconds=hourly.Interval()
        ),
        inclusive="left"
    )

    # --------------------------------------------------------
    # CREATE DATAFRAME
    # --------------------------------------------------------

    data = pd.DataFrame({

        "date": time,

        "station_id": station_id,

        "station_name": station_name,

        "latitude": response.Latitude(),

        "longitude": response.Longitude(),

        "temperature": (
            hourly.Variables(0).ValuesAsNumpy()
        ),

        "humidity": (
            hourly.Variables(1).ValuesAsNumpy()
        ),

        "pressure": (
            hourly.Variables(2).ValuesAsNumpy()
        ),

        "wind_speed": (
            hourly.Variables(3).ValuesAsNumpy()
        ),

        "precipitation": (
            hourly.Variables(4).ValuesAsNumpy()
        ),

        "rain": (
            hourly.Variables(5).ValuesAsNumpy()
        )
    })

    # --------------------------------------------------------
    # CONVERT UTC → INDIA TIME
    # --------------------------------------------------------

    data["date"] = (
        data["date"]
        .dt.tz_convert("Asia/Kolkata")
    )

    # --------------------------------------------------------
    # REMOVE FUTURE TIMESTAMPS
    # --------------------------------------------------------
    #
    # This is the important safety check.
    #
    # Even if Open-Meteo returns a forecast timestamp,
    # SkyGuard will not treat it as an observed reading.
    #
    # Only:
    #
    #       timestamp <= current India time
    #
    # is retained.
    # --------------------------------------------------------

    data = data[
        data["date"] <= now_india
    ].copy()

    # --------------------------------------------------------
    # SORT OLDEST → NEWEST
    # --------------------------------------------------------

    data = (
        data
        .sort_values("date")
        .reset_index(drop=True)
    )

    return data


# ------------------------------------------------------------
# PROCESS STATION A
# ------------------------------------------------------------

primary_data = process_station(
    responses[0],
    "STATION_A",
    "Primary Station"
)


# ------------------------------------------------------------
# PROCESS STATION B
# ------------------------------------------------------------

reference_data = process_station(
    responses[1],
    "STATION_B",
    "Comparison Station 1"
)


# ------------------------------------------------------------
# PROCESS STATION C
# ------------------------------------------------------------

comparison_data = process_station(
    responses[2],
    "STATION_C",
    "Comparison Station 2"
)


# ------------------------------------------------------------
# PRINT STATION INFORMATION
# ------------------------------------------------------------

print()
print("-" * 60)
print("STATION A - PRIMARY")
print("-" * 60)

print(
    "Coordinates:",
    responses[0].Latitude(),
    "N",
    responses[0].Longitude(),
    "E"
)

print(
    "Elevation:",
    responses[0].Elevation(),
    "m"
)


print()
print("-" * 60)
print("STATION B - COMPARISON 1")
print("-" * 60)

print(
    "Coordinates:",
    responses[1].Latitude(),
    "N",
    responses[1].Longitude(),
    "E"
)

print(
    "Elevation:",
    responses[1].Elevation(),
    "m"
)


print()
print("-" * 60)
print("STATION C - COMPARISON 2")
print("-" * 60)

print(
    "Coordinates:",
    responses[2].Latitude(),
    "N",
    responses[2].Longitude(),
    "E"
)

print(
    "Elevation:",
    responses[2].Elevation(),
    "m"
)


# ------------------------------------------------------------
# SAVE FILES
# ------------------------------------------------------------

primary_file = (
    project_folder / "weather_data.csv"
)

reference_file = (
    project_folder / "reference_station_data.csv"
)

comparison_file = (
    project_folder / "comparison_station_data.csv"
)


primary_data.to_csv(
    primary_file,
    index=False
)

reference_data.to_csv(
    reference_file,
    index=False
)

comparison_data.to_csv(
    comparison_file,
    index=False
)


# ------------------------------------------------------------
# PRIMARY DATA
# ------------------------------------------------------------

print()
print("=" * 60)
print("       PRIMARY STATION DATA")
print("=" * 60)

print(
    primary_data.head()
)

print()
print(
    "Total primary readings:",
    len(primary_data)
)

if len(primary_data) > 0:

    print(
        "Oldest primary reading:",
        primary_data["date"].min()
    )

    print(
        "Latest primary reading:",
        primary_data["date"].max()
    )


# ------------------------------------------------------------
# COMPARISON STATION 1
# ------------------------------------------------------------

print()
print("=" * 60)
print("       COMPARISON STATION 1 DATA")
print("=" * 60)

print(
    reference_data.head()
)

print()
print(
    "Total comparison 1 readings:",
    len(reference_data)
)

if len(reference_data) > 0:

    print(
        "Oldest comparison 1 reading:",
        reference_data["date"].min()
    )

    print(
        "Latest comparison 1 reading:",
        reference_data["date"].max()
    )


# ------------------------------------------------------------
# COMPARISON STATION 2
# ------------------------------------------------------------

print()
print("=" * 60)
print("       COMPARISON STATION 2 DATA")
print("=" * 60)

print(
    comparison_data.head()
)

print()
print(
    "Total comparison 2 readings:",
    len(comparison_data)
)

if len(comparison_data) > 0:

    print(
        "Oldest comparison 2 reading:",
        comparison_data["date"].min()
    )

    print(
        "Latest comparison 2 reading:",
        comparison_data["date"].max()
    )


# ------------------------------------------------------------
# FINAL FUTURE-DATA SAFETY CHECK
# ------------------------------------------------------------

print()
print("=" * 60)
print("          FUTURE DATA SAFETY CHECK")
print("=" * 60)

for station_name, station_data in [
    ("STATION_A", primary_data),
    ("STATION_B", reference_data),
    ("STATION_C", comparison_data)
]:

    future_rows = (
        station_data["date"] > now_india
    ).sum()

    print()
    print(
        station_name,
        "future rows:",
        future_rows
    )

    if future_rows == 0:
        print(
            "STATUS: OK - no future readings stored"
        )
    else:
        print(
            "STATUS: WARNING - future readings detected"
        )


# ------------------------------------------------------------
# FILE INFORMATION
# ------------------------------------------------------------

print()
print("=" * 60)
print("             FILES CREATED")
print("=" * 60)

print()
print("Primary station:")
print("weather_data.csv")

print()
print("Comparison station 1:")
print("reference_station_data.csv")

print()
print("Comparison station 2:")
print("comparison_station_data.csv")


# ------------------------------------------------------------
# STATION INFORMATION
# ------------------------------------------------------------

print()
print("=" * 60)
print("          STATION INFORMATION")
print("=" * 60)

print()
print(
    "STATION_A:",
    responses[0].Latitude(),
    responses[0].Longitude()
)

print(
    "STATION_B:",
    responses[1].Latitude(),
    responses[1].Longitude()
)

print(
    "STATION_C:",
    responses[2].Latitude(),
    responses[2].Longitude()
)


# ------------------------------------------------------------
# FINAL MESSAGE
# ------------------------------------------------------------

print()
print("=" * 60)
print("       WEATHER DATA COLLECTION COMPLETED")
print("=" * 60)

print()
print("SkyGuard is using:")
print("PAST DATA + CURRENT AVAILABLE DATA")
print("NOT FUTURE FORECAST DATA")
print()
