/**
 * Sorting utilities for the Lecturer Dashboard.
 */

/** Maps risk levels to a numeric order for sorting (High first). */
export const RISK_ORDER = { High: 0, Medium: 1, Low: 2 }

/**
 * Return a new sorted copy of the student list.
 *
 * @param {Array}   list      - Array of student objects.
 * @param {string}  sortKey   - 'risk_level' or 'name'.
 * @param {boolean} ascending - true for ascending, false for descending.
 * @returns {Array} A new sorted array (original is never mutated).
 */
export function sortStudents(list, sortKey, ascending) {
  return [...list].sort((a, b) => {
    let cmp = 0
    if (sortKey === 'risk_level') {
      cmp = RISK_ORDER[a.risk_level] - RISK_ORDER[b.risk_level]
      if (cmp === 0) cmp = a.name.localeCompare(b.name) // tiebreaker
    } else if (sortKey === 'name') {
      cmp = a.name.localeCompare(b.name)
    }
    return ascending ? cmp : -cmp
  })
}
