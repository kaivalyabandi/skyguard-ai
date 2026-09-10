import pandas as pd

# Read the real weather data
data = pd.read_csv("weather_data.csv")

# Make a copy
test_data = data.copy()

# Add artificial anomalies to specific rows
test_data.loc[10, "temperature"] = 55
test_data.loc[30, "temperature"] = -10

test_data.loc[50, "humidity"] = 150
test_data.loc[70, "humidity"] = -20

test_data.loc[90, "pressure"] = 1100
test_data.loc[110, "pressure"] = 850

test_data.loc[130, "wind_speed"] = 150
test_data.loc[150, "precipitation"] = 100

# Save the modified data
test_data.to_csv("weather_test_data.csv", index=False)

print("Artificial anomalies added successfully!")
print("File created: weather_test_data.csv")

# Display the rows we changed
print("\nInjected anomaly rows:")
print(test_data.loc[[10, 30, 50, 70, 90, 110, 130, 150]])