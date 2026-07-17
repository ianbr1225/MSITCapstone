import { useEffect, useMemo, useState } from 'react'
import styles from './LecturerDashboard.module.css'
import { sortStudents } from '../utils/sortStudents.js'

const API_URL = 'http://localhost:8000/api/risk-list'


// ── Component ───────────────────────────────────────────────────────
export default function LecturerDashboard() {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Sort state — defaults to Risk Level, High → Low (ascending order map)
  const [sortKey, setSortKey] = useState('risk_level')
  const [sortAsc, setSortAsc] = useState(true)

  useEffect(() => {
    // TODO: remove artificial delay, added for demo purposes
    const DEMO_DELAY_MS = 700

    fetch(API_URL)
      .then((res) => {
        if (!res.ok) throw new Error(`Server responded with ${res.status}`)
        return res.json()
      })
      .then((data) => {
        // TODO: remove artificial delay, added for demo purposes
        return new Promise((resolve) =>
          setTimeout(() => resolve(data), DEMO_DELAY_MS)
        )
      })
      .then((data) => {
        setStudents(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  const sorted = useMemo(
    () => sortStudents(students, sortKey, sortAsc),
    [students, sortKey, sortAsc]
  )

  // Toggle sort when a column header is clicked
  function handleSort(key) {
    if (sortKey === key) {
      setSortAsc((prev) => !prev)
    } else {
      setSortKey(key)
      setSortAsc(true)
    }
  }

  // Small arrow indicator for the active sort column
  function sortIndicator(key) {
    if (sortKey !== key) return null
    return <span className={styles.sortArrow}>{sortAsc ? ' ▲' : ' ▼'}</span>
  }

  return (
    <div className={styles.wrapper}>
      <header className={styles.header}>
        <h1 className={styles.title}>Lecturer Dashboard</h1>
        <p className={styles.subtitle}>Student Risk Overview</p>
      </header>

      {loading && (
        <div className={styles.statusBox}>
          <span className={styles.spinner} aria-label="Loading" />
          <p>Loading student data…</p>
        </div>
      )}

      {error && (
        <div className={`${styles.statusBox} ${styles.errorBox}`}>
          <p>
            <strong>Unable to load data.</strong> Make sure the backend is
            running on port 8000.
          </p>
          <p className={styles.errorDetail}>{error}</p>
        </div>
      )}

      {!loading && !error && (
        <div className={styles.tableContainer}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th
                  className={styles.sortable}
                  onClick={() => handleSort('name')}
                >
                  Name{sortIndicator('name')}
                </th>
                <th
                  className={styles.sortable}
                  onClick={() => handleSort('risk_level')}
                >
                  Risk Level{sortIndicator('risk_level')}
                </th>
                <th>Engagement Score</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((s, idx) => (
                <tr
                  key={s.name}
                  className={`${styles[`row${s.risk_level}`]} ${styles.rowAnimated}`}
                  style={{ animationDelay: `${idx * 50}ms` }}
                >
                  <td>{s.name}</td>
                  <td>
                    <span className={`${styles.badge} ${styles[`badge${s.risk_level}`]}`}>
                      {s.risk_level}
                    </span>
                  </td>
                  <td className={styles.score}>{s.engagement_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
