import { useEffect, useMemo, useRef, useState } from 'react'
import { supabase } from './lib/supabaseClient'
import './App.css'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

function App() {
  const [stations, setStations] = useState([])
  const [anomalies, setAnomalies] = useState([])
  const [selectedAnomaly, setSelectedAnomaly] = useState(null)
  const anomalyDetailsRef = useRef(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    setLoading(true)
    setError('')

    const { data: stationData, error: stationError } = await supabase
      .from('stations')
      .select('*')

    const { data: anomalyData, error: anomalyError } = await supabase
      .from('anomaly_results')
      .select('*')
      .order('timestamp', { ascending: false })

    if (stationError) {
      console.error('Station error:', stationError)
      setError('Unable to load station data.')
    }

    if (anomalyError) {
      console.error('Anomaly error:', anomalyError)
      setError('Unable to load anomaly data.')
    }

    setStations(stationData || [])
    setAnomalies(anomalyData || [])
    setLoading(false)
  }

  const total = anomalies.length

  const normal = anomalies.filter(
    item => item.final_status === 'NORMAL'
  ).length

  const possibleAnomalies = anomalies.filter(
    item => item.final_status === 'POSSIBLE ANOMALY'
  ).length

  const sensorFaults = anomalies.filter(
    item => item.final_status === 'SENSOR FAULT'
  ).length

  const highCritical = anomalies.filter(
    item =>
      item.severity === 'HIGH' ||
      item.severity === 'CRITICAL'
  ).length

  const abnormalReadings = useMemo(() => {
    return anomalies
      .filter(item => item.final_status !== 'NORMAL')
      .sort((a, b) => {
        const severityRank = {
          CRITICAL: 1,
          HIGH: 2,
          MEDIUM: 3,
          LOW: 4,
          NORMAL: 5
        }

        const severityA =
          severityRank[a.severity] || 6

        const severityB =
          severityRank[b.severity] || 6

        if (severityA !== severityB) {
          return severityA - severityB
        }

        return (
          new Date(b.timestamp) -
          new Date(a.timestamp)
        )
      })
  }, [anomalies])

  const displayReadings = useMemo(() => {
    return [...anomalies]
      .sort((a, b) => {
        const aIsAbnormal = a.final_status !== 'NORMAL' ? 1 : 0
        const bIsAbnormal = b.final_status !== 'NORMAL' ? 1 : 0

        if (aIsAbnormal !== bIsAbnormal) {
          return bIsAbnormal - aIsAbnormal
        }

        return new Date(b.timestamp) - new Date(a.timestamp)
      })
      .slice(0, 20)
  }, [anomalies])

  function handleSelectAnomaly(item) {
    setSelectedAnomaly(item)

    setTimeout(() => {
      anomalyDetailsRef.current?.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      })
    }, 100)
  }

  function getStatusClass(status) {
    if (status === 'SENSOR FAULT') return 'status-fault'
    if (status === 'POSSIBLE ANOMALY') return 'status-warning'
    return 'status-normal'
  }

  function getSeverityClass(severity) {
    if (severity === 'CRITICAL') return 'severity-critical'
    if (severity === 'HIGH') return 'severity-high'
    if (severity === 'MEDIUM') return 'severity-medium'
    if (severity === 'LOW') return 'severity-low'
    return 'severity-normal'
  }

  function formatTimestamp(timestamp) {
    if (!timestamp) return '—'

    return new Date(timestamp).toLocaleString('en-IN', {
      dateStyle: 'medium',
      timeStyle: 'short'
    })
  }

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <h2>Loading SkyGuard AI...</h2>
        <p>Connecting to weather intelligence system</p>
      </div>
    )
  }

  return (
    <div className="app">

      {/* HEADER */}

      <header className="topbar">

        <div className="brand">

          <div className="brand-icon">
            SG
          </div>

          <div>
            <h1>SkyGuard AI</h1>
            <p>
              Intelligent Weather Anomaly Detection
            </p>
          </div>

        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          System Online
        </div>

      </header>


      {/* MAIN CONTENT */}

      <main className="dashboard">

        {error && (
          <div className="error-banner">
            ⚠ {error}
          </div>
        )}


        {/* HERO */}

        <section className="hero">

          <div>

            <p className="eyebrow">
              REAL-TIME WEATHER INTELLIGENCE
            </p>

            <h2>
              Monitor. Detect. Respond.
            </h2>

            <p className="hero-description">
              SkyGuard AI continuously analyzes
              temperature, humidity and atmospheric
              pressure to identify abnormal weather
              readings and potential sensor faults.
            </p>

          </div>

          <div className="hero-badge">
            <span>AI ENGINE</span>
            <strong>ACTIVE</strong>
          </div>

        </section>


        {/* SUMMARY CARDS */}

        <section className="stats-grid">

          <div className="stat-card">
            <div className="stat-label">
              TOTAL READINGS
            </div>
            <div className="stat-value">
              {total}
            </div>
            <div className="stat-subtext">
              Weather observations
            </div>
          </div>


          <div className="stat-card normal-card">
            <div className="stat-label">
              NORMAL
            </div>
            <div className="stat-value">
              {normal}
            </div>
            <div className="stat-subtext">
              Healthy readings
            </div>
          </div>


          <div className="stat-card warning-card">
            <div className="stat-label">
              POSSIBLE ANOMALIES
            </div>
            <div className="stat-value">
              {possibleAnomalies}
            </div>
            <div className="stat-subtext">
              Requires attention
            </div>
          </div>


          <div className="stat-card fault-card">
            <div className="stat-label">
              SENSOR FAULTS
            </div>
            <div className="stat-value">
              {sensorFaults}
            </div>
            <div className="stat-subtext">
              Detected faults
            </div>
          </div>


          <div className="stat-card critical-card">
            <div className="stat-label">
              HIGH / CRITICAL
            </div>
            <div className="stat-value">
              {highCritical}
            </div>
            <div className="stat-subtext">
              Priority alerts
            </div>
          </div>

        </section>


        {/* STATIONS */}

        <section className="section">

          <div className="section-heading">

            <div>
              <p className="eyebrow">
                MONITORING NETWORK
              </p>

              <h2>Weather Stations</h2>
            </div>

            <span className="station-count">
              {stations.length} stations
            </span>

          </div>


          <div className="stations-grid">

            {stations.map(station => (

              <div
                className="station-card"
                key={station.station_id}
              >

                <div className="station-top">

                  <div className="station-icon">
                    {station.station_id === 'STATION_A'
                      ? 'A'
                      : station.station_id === 'STATION_B'
                      ? 'B'
                      : 'C'}
                  </div>

                  <span
                    className={
                      station.role === 'PRIMARY'
                        ? 'role-primary'
                        : 'role-comparison'
                    }
                  >
                    {station.role}
                  </span>

                </div>


                <h3>
                  {station.station_name}
                </h3>

                <p className="station-id">
                  {station.station_id}
                </p>

                <div className="coordinates">

                  <span>
                    LAT&nbsp;
                    {Number(station.latitude).toFixed(4)}
                  </span>

                  <span>
                    LON&nbsp;
                    {Number(station.longitude).toFixed(4)}
                  </span>

                </div>

              </div>

            ))}

          </div>

        </section>
        {/* MAP */}

        <section className="section">

          <div className="section-heading">

            <div>
              <p className="eyebrow">
                STATION LOCATION
              </p>

              <h2>Weather Station Map</h2>
            </div>

            <span className="station-count">
              3 stations
            </span>

          </div>

          <div className="map-container">

            <MapContainer
              center={[17.6868, 83.1100]}
              zoom={11}
              scrollWheelZoom={false}
              style={{ height: '420px', width: '100%' }}
            >

              <TileLayer
                attribution='&copy; OpenStreetMap contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              <Marker position={[17.6868, 83.2185]}>
                <Popup>
                  <strong>STATION_A</strong>
                  <br />
                  Primary Station
                  <br />
                  Lat: 17.6868
                  <br />
                  Lon: 83.2185
                </Popup>
              </Marker>

              <Marker position={[17.6913, 83.0039]}>
                <Popup>
                  <strong>STATION_B</strong>
                  <br />
                  Comparison 1
                  <br />
                  Lat: 17.6913
                  <br />
                  Lon: 83.0039
                </Popup>
              </Marker>

              <Marker position={[17.7000, 83.1000]}>
                <Popup>
                  <strong>STATION_C</strong>
                  <br />
                  Comparison 2
                  <br />
                  Lat: 17.7000
                  <br />
                  Lon: 83.1000
                </Popup>
              </Marker>

            </MapContainer>

          </div>

        </section>
         {/* 3-STATION COMPARISON */}

        <section className="section">

          <div className="section-heading">
            <div>
              <p className="eyebrow">
                SPATIAL ANALYSIS
              </p>

              <h2>3-Station Comparison</h2>
            </div>

            <span className="station-count">
              A vs B + C
            </span>
          </div>


          <div className="comparison-card">

            <div className="comparison-station">
              <div className="comparison-icon primary">
                A
              </div>

              <div>
                <strong>STATION_A</strong>
                <span>Primary Station</span>
              </div>
            </div>


            <div className="comparison-arrow">
              compared with
            </div>


            <div className="comparison-station">
              <div className="comparison-icon">
                B
              </div>

              <div>
                <strong>STATION_B</strong>
                <span>Comparison 1</span>
              </div>
            </div>


            <div className="comparison-plus">
              +
            </div>


            <div className="comparison-station">
              <div className="comparison-icon">
                C
              </div>

              <div>
                <strong>STATION_C</strong>
                <span>Comparison 2</span>
              </div>
            </div>


            <div className="comparison-result">
              <span>SPATIAL ANALYSIS RESULT</span>

              <strong>
                STATION A → B + C
              </strong>

              <p>
                Primary station is evaluated against
                both comparison stations to identify
                possible spatial outliers.
              </p>
            </div>

          </div>

        </section>



        {/* ALERTS */}

        <section className="section">

          <div className="section-heading">

            <div>
              <p className="eyebrow">
                AI DETECTION ENGINE
              </p>

              <h2>Active Anomaly Alerts</h2>
            </div>

            <span className="alert-count">
              {abnormalReadings.length} detected
            </span>

          </div>


          {abnormalReadings.length === 0 ? (

            <div className="empty-state">
              <div className="empty-icon">
                ✓
              </div>

              <h3>
                No active anomalies
              </h3>

              <p>
                All monitored readings are currently
                within expected ranges.
              </p>
            </div>

          ) : (

            <div className="alerts-list">

              {abnormalReadings
                .slice(0, 12)
                .map(item => (

                  <div
                    className="alert-card"
                    key={item.id}
                    onClick={() => handleSelectAnomaly(item)}
                     role="button"
  tabIndex={0}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleSelectAnomaly(item)
    }
  }}
                  >

                    <div className="alert-main">

                      <div
                        className={
                          'alert-indicator ' +
                          getSeverityClass(item.severity)
                        }
                      >
                        !
                      </div>


                      <div className="alert-content">

                        <div className="alert-title-row">

                          <h3>
                            {item.fault_type || 'Anomaly detected'}
                          </h3>

                          <span
                            className={
                              'status-badge ' +
                              getStatusClass(
                                item.final_status
                              )
                            }
                          >
                            {item.final_status}
                          </span>

                        </div>


                        <p className="alert-reason">
                          {item.reason ||
                            'Abnormal weather reading detected.'}
                        </p>


                        <div className="alert-meta">

                          <span>
                            {formatTimestamp(
                              item.timestamp
                            )}
                          </span>

                          <span>
                            {item.station_id}
                          </span>

                          <span>
                            Confidence:
                            {' '}
                            {item.confidence_percent || 0}%
                          </span>
                          <span className="view-details">
  Click to view details →
</span>

                        </div>

                      </div>

                    </div>


                    <div className="alert-side">

                      <span
                        className={
                          'severity-badge ' +
                          getSeverityClass(
                            item.severity
                          )
                        }
                      >
                        {item.severity}
                      </span>

                    </div>

                  </div>

                ))}

            </div>

          )}

        </section>
                {/* ANOMALY DETAILS */}

        {selectedAnomaly && (
          <section
            className="section anomaly-details-section"
            ref={anomalyDetailsRef}
          >

            <div className="section-heading">

              <div>
                <p className="eyebrow">
                  SELECTED ALERT
                </p>

                <h2>
                  Anomaly Details
                </h2>
              </div>

              <button
                className="close-details"
                onClick={() => setSelectedAnomaly(null)}
              >
                Close
              </button>

            </div>


            <div className="anomaly-details-card">

              <div className="detail-header">

                <div>
                  <h3>
                    {selectedAnomaly.fault_type || 'Anomaly detected'}
                  </h3>

                  <p>
                    Station: {selectedAnomaly.station_id || 'Unknown'}
                  </p>
                </div>


                <span
                  className={
                    'status-badge ' +
                    getStatusClass(selectedAnomaly.final_status)
                  }
                >
                  {selectedAnomaly.final_status || 'Unknown'}
                </span>

              </div>


              <div className="details-grid">

                <div className="detail-item">
                  <span>Temperature</span>
                  <strong>
                    {selectedAnomaly.temperature != null
                      ? `${Number(selectedAnomaly.temperature).toFixed(2)} °C`
                      : '—'}
                  </strong>
                </div>


                <div className="detail-item">
                  <span>Humidity</span>
                  <strong>
                    {selectedAnomaly.humidity != null
                      ? `${Number(selectedAnomaly.humidity).toFixed(2)} %`
                      : '—'}
                  </strong>
                </div>


                <div className="detail-item">
                  <span>Pressure</span>
                  <strong>
                    {selectedAnomaly.pressure != null
                      ? `${Number(selectedAnomaly.pressure).toFixed(2)} hPa`
                      : '—'}
                  </strong>
                </div>


                <div className="detail-item">
                  <span>Confidence</span>
                  <strong>
                    {selectedAnomaly.confidence_percent != null
                      ? `${selectedAnomaly.confidence_percent}%`
                      : '—'}
                  </strong>
                </div>


                <div className="detail-item">
                  <span>Severity</span>
                  <strong>
                    {selectedAnomaly.severity || '—'}
                  </strong>
                </div>


                <div className="detail-item">
                  <span>Timestamp</span>
                  <strong>
                    {selectedAnomaly.timestamp
                      ? new Date(selectedAnomaly.timestamp).toLocaleString()
                      : '—'}
                  </strong>
                </div>

              </div>


             <div className="detail-text">

  <div>
    <span>Fault Type</span>
    <p>
      {selectedAnomaly.fault_type || '—'}
    </p>
  </div>

  <div>
    <span>Reason</span>
    <p>
      {selectedAnomaly.reason || 'No reason provided'}
    </p>
  </div>

  <div>
    <span>Recommendation</span>
    <p>
      {selectedAnomaly.recommendation ||
        'No recommendation available'}
    </p>
  </div>

  <div>
    <span>Temporal Result</span>
    <p>
      {selectedAnomaly.temporal_result ||
        'No temporal analysis available'}
    </p>
  </div>

  <div>
    <span>Spatial Result</span>
    <p>
      {selectedAnomaly.spatial_result ||
        'No spatial analysis available'}
    </p>
  </div>

  <div>
    <span>Cross-Sensor Result</span>
    <p>
      {selectedAnomaly.cross_sensor_result ||
        'No cross-sensor analysis available'}
    </p>
  </div>

  <div>
    <span>Evidence Count</span>
    <p>
      {selectedAnomaly.evidence_count ?? '—'}
    </p>
  </div>

</div>
            </div>

          </section>
        )}


        {/* DATA TABLE */}

        <section className="section">

          <div className="section-heading">

            <div>
              <p className="eyebrow">
                SENSOR DATA
              </p>

              <h2>Recent Readings</h2>
            </div>

          </div>


          <div className="table-container">

            <table>

              <thead>

                <tr>
                  <th>TIME</th>
                  <th>STATION</th>
                  <th>TEMP</th>
                  <th>HUMIDITY</th>
                  <th>PRESSURE</th>
                  <th>STATUS</th>
                  <th>FAULT</th>
                  <th>CONFIDENCE</th>
                  <th>SEVERITY</th>
                </tr>

              </thead>


              <tbody>

                {displayReadings.map(item => (

                    <tr key={item.id}>

                      <td>
                        {formatTimestamp(
                          item.timestamp
                        )}
                      </td>

                      <td>
                        <strong>
                          {item.station_id}
                        </strong>
                      </td>

                      <td>
                        {item.temperature?.toFixed(2)} °C
                      </td>

                      <td>
                        {item.humidity?.toFixed(2)} %
                      </td>

                      <td>
                        {item.pressure?.toFixed(2)} hPa
                      </td>

                      <td>
                        <span
                          className={
                            'status-badge ' +
                            getStatusClass(
                              item.final_status
                            )
                          }
                        >
                          {item.final_status}
                        </span>
                      </td>

                      <td>
                        {item.fault_type || 'NONE'}
                      </td>

                      <td>
                        {item.confidence_percent || 0}%
                      </td>

                      <td>
                        <span
                          className={
                            'severity-badge ' +
                            getSeverityClass(
                              item.severity
                            )
                          }
                        >
                          {item.severity}
                        </span>
                      </td>

                    </tr>

                  ))}

              </tbody>

            </table>

          </div>

        </section>


        {/* FOOTER */}

        <footer>

          <div>
            <strong>SkyGuard AI</strong>
            <span>
              &nbsp; • &nbsp; Weather Intelligence Platform
            </span>
          </div>

          <span>
            AI anomaly detection active
          </span>

        </footer>

      </main>

    </div>
  )
}

export default App