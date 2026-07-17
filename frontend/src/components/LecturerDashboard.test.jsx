/**
 * Component-level tests for LecturerDashboard.
 * Mocks fetch to test loading, success, and error states.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import LecturerDashboard from './LecturerDashboard.jsx'

const MOCK_API_DATA = [
  { name: 'Alice Johnson',  risk_level: 'High',   engagement_score: 23 },
  { name: 'Brian Lee',      risk_level: 'Low',    engagement_score: 87 },
  { name: 'Carmen Rivera',  risk_level: 'Medium', engagement_score: 54 },
]

beforeEach(() => {
  vi.restoreAllMocks()
})

afterEach(() => {
  vi.restoreAllMocks()
})

// ── Loading state ───────────────────────────────────────────────────

describe('LecturerDashboard loading state', () => {
  it('shows loading text before fetch resolves', () => {
    // fetch that never resolves
    vi.stubGlobal('fetch', () => new Promise(() => {}))

    render(<LecturerDashboard />)
    expect(screen.getByText(/loading student data/i)).toBeInTheDocument()
  })
})

// ── Success state ───────────────────────────────────────────────────

describe('LecturerDashboard success state', () => {
  it('renders student rows after fetch resolves', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(MOCK_API_DATA),
        })
      )
    )

    render(<LecturerDashboard />)

    await waitFor(() => {
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
    })

    expect(screen.getByText('Brian Lee')).toBeInTheDocument()
    expect(screen.getByText('Carmen Rivera')).toBeInTheDocument()
  })
})

// ── Error state ─────────────────────────────────────────────────────

describe('LecturerDashboard error state', () => {
  it('renders error message on fetch rejection', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.reject(new Error('Network failure')))
    )

    render(<LecturerDashboard />)

    await waitFor(() => {
      expect(screen.getByText(/unable to load data/i)).toBeInTheDocument()
    })

    expect(screen.getByText('Network failure')).toBeInTheDocument()
  })

  it('renders error message on non-ok HTTP response', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() =>
        Promise.resolve({
          ok: false,
          status: 500,
        })
      )
    )

    render(<LecturerDashboard />)

    await waitFor(() => {
      expect(screen.getByText(/unable to load data/i)).toBeInTheDocument()
    })
  })
})
