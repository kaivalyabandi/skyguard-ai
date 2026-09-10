# skyguard-ai
AI-powered anomaly detection and sensor health monitoring for Automatic Weather Stations.
# SkyGuard AI 🌦️

### Intelligent Real-Time Anomaly Detection for Automatic Weather Stations

SkyGuard AI is an AI/ML-based weather monitoring and anomaly detection system designed to identify abnormal or faulty readings from Automatic Weather Stations (AWS).

The system analyzes **temperature, atmospheric pressure, and humidity** data to detect unusual patterns such as sensor spikes, drift, flatline readings, bias, and data dropouts. Instead of treating every unusual reading as a genuine weather event, SkyGuard combines multiple validation techniques to distinguish **real environmental events from sensor or data faults**.

---

## 🚨 Problem

Automatic Weather Stations continuously collect environmental data, but sensor readings can become unreliable due to:

- Sensor malfunction
- Calibration errors
- Communication failures
- Power fluctuations
- Harsh environmental conditions
- Data corruption
- Sudden abnormal readings

A simple threshold-based system may generate unnecessary false alarms.

**SkyGuard AI aims to detect anomalies while providing additional validation before classifying a reading as a genuine weather event or a sensor/data fault.**

---

## 💡 Solution

SkyGuard AI follows a multi-stage anomaly detection pipeline:

**AWS Weather Data → Data Validation → Isolation Forest → Temporal Analysis → Cross-Sensor Analysis → Spatial Validation → Decision Engine → Fault Classification → Explanation → Dashboard**

The system follows the principle:

> **A flag is not a verdict.**

An anomalous reading is first detected and then validated using additional contextual information before a final decision is made.

---

## 🔍 Key Features

- Real-time weather data monitoring
- Temperature, pressure and humidity analysis
- Machine-learning-based anomaly detection
- Isolation Forest anomaly detection
- Temporal pattern analysis
- Cross-sensor validation
- Spatial/station comparison
- Sensor fault classification
- Confidence and severity information
- Explainable anomaly insights
- Interactive monitoring dashboard
- Weather event simulation
- Fault simulation
- Sensor blackout simulation

---

## 🤖 Machine Learning

SkyGuard AI uses the **Isolation Forest** algorithm for unsupervised anomaly detection.

The model analyzes multiple weather parameters together:

- Temperature
- Atmospheric Pressure
- Humidity

This allows the system to identify observations that differ significantly from normal patterns without requiring a large labelled fault dataset.

The detected anomalies are then passed through additional validation and decision logic.

---

## 🧠 Fault Detection

The system can identify different types of abnormal sensor behaviour, including:

- **Spike** – sudden abnormal change in a reading
- **Drift** – gradual movement away from expected values
- **Flatline** – sensor repeatedly producing the same value
- **Bias** – consistently shifted readings
- **Dropout** – missing or interrupted sensor data

The system also considers whether an unusual reading may represent a genuine environmental event rather than a sensor failure.

---

## 🗣️ Explainable AI

SkyGuard uses **Groq** to generate natural-language explanations of detected anomalies.

Groq is used for **explanation**, not for making the core anomaly decision.

The deterministic detection and decision pipeline determines the result, while the language model helps explain the result in a way that is easier for an operator to understand.

---

## 📊 Dashboard

The SkyGuard command-center dashboard provides a visual view of:

- Weather station locations
- Live telemetry
- Anomaly alerts
- Station health
- Operator attention
- Transmission information
- System status
- Simulation controls

The dashboard is built using **React and Vite**.

---

## 🌐 Data Source

The prototype uses weather data obtained from **Open-Meteo**.

Fault conditions are also simulated and injected into weather data so that the anomaly-detection pipeline can be tested against different sensor-failure scenarios.

---

## 🛠️ Technology Stack

### Machine Learning & Data
- Python
- Pandas
- NumPy
- Scikit-learn
- Isolation Forest

### Frontend
- React
- Vite
- React Leaflet
- Leaflet
- OpenStreetMap

### Database
- Supabase

### Explainability
- Groq API

### Deployment
- Vercel

---

## 🔄 System Workflow

```text
Weather Data
     ↓
Data Validation
     ↓
Isolation Forest
     ↓
Temporal Analysis
     ↓
Cross-Sensor Analysis
     ↓
Spatial Validation
     ↓
Decision Engine
     ↓
Fault Classification
     ↓
Explainability
     ↓
Monitoring Dashboard
