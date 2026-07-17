/**
 * White-box unit tests for sortStudents utility.
 * Tests sorting logic directly — no component rendering, no DOM.
 */

import { describe, it, expect } from 'vitest'
import { sortStudents } from './sortStudents.js'

// ── Test fixtures ───────────────────────────────────────────────────

const STUDENTS = [
  { name: 'Carmen Rivera',  risk_level: 'Medium', engagement_score: 54 },
  { name: 'Alice Johnson',  risk_level: 'High',   engagement_score: 23 },
  { name: 'Elena Martinez', risk_level: 'Low',    engagement_score: 91 },
  { name: 'Brian Lee',      risk_level: 'Low',    engagement_score: 87 },
  { name: 'David Okonkwo',  risk_level: 'High',   engagement_score: 18 },
]

// ── Sort by risk_level ──────────────────────────────────────────────

describe('sortStudents by risk_level', () => {
  it('ascending: High → Medium → Low', () => {
    const sorted = sortStudents(STUDENTS, 'risk_level', true)
    const levels = sorted.map((s) => s.risk_level)
    expect(levels).toEqual(['High', 'High', 'Medium', 'Low', 'Low'])
  })

  it('descending: Low → Medium → High', () => {
    const sorted = sortStudents(STUDENTS, 'risk_level', false)
    const levels = sorted.map((s) => s.risk_level)
    expect(levels).toEqual(['Low', 'Low', 'Medium', 'High', 'High'])
  })
})

// ── Sort by name ────────────────────────────────────────────────────

describe('sortStudents by name', () => {
  it('ascending: alphabetical A → Z', () => {
    const sorted = sortStudents(STUDENTS, 'name', true)
    const names = sorted.map((s) => s.name)
    expect(names).toEqual([
      'Alice Johnson',
      'Brian Lee',
      'Carmen Rivera',
      'David Okonkwo',
      'Elena Martinez',
    ])
  })

  it('descending: alphabetical Z → A', () => {
    const sorted = sortStudents(STUDENTS, 'name', false)
    const names = sorted.map((s) => s.name)
    expect(names).toEqual([
      'Elena Martinez',
      'David Okonkwo',
      'Carmen Rivera',
      'Brian Lee',
      'Alice Johnson',
    ])
  })
})

// ── Tiebreaker ──────────────────────────────────────────────────────

describe('sortStudents tiebreaker', () => {
  it('equal risk_level falls back to name sort (ascending)', () => {
    const sorted = sortStudents(STUDENTS, 'risk_level', true)
    // Both High-risk students should be ordered by name
    const highRisk = sorted.filter((s) => s.risk_level === 'High')
    expect(highRisk.map((s) => s.name)).toEqual([
      'Alice Johnson',
      'David Okonkwo',
    ])
    // Both Low-risk students should be ordered by name
    const lowRisk = sorted.filter((s) => s.risk_level === 'Low')
    expect(lowRisk.map((s) => s.name)).toEqual([
      'Brian Lee',
      'Elena Martinez',
    ])
  })

  it('equal risk_level falls back to name sort (descending)', () => {
    const sorted = sortStudents(STUDENTS, 'risk_level', false)
    // In descending, Low comes first — within Low, names are reversed
    const lowRisk = sorted.filter((s) => s.risk_level === 'Low')
    expect(lowRisk.map((s) => s.name)).toEqual([
      'Elena Martinez',
      'Brian Lee',
    ])
  })
})

// ── Immutability ────────────────────────────────────────────────────

describe('sortStudents immutability', () => {
  it('does not mutate the original array', () => {
    const original = [...STUDENTS]
    const copy = STUDENTS.map((s) => ({ ...s }))
    sortStudents(original, 'risk_level', true)
    expect(original).toEqual(copy)
  })

  it('returns a new array reference', () => {
    const result = sortStudents(STUDENTS, 'risk_level', true)
    expect(result).not.toBe(STUDENTS)
  })
})
