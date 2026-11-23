export const PHASES = ['powerplay', 'middle', 'death', 'other']

// Seasons offered in dropdowns (newest first)
export const SEASONS = Array.from({ length: 18 }, (_, i) => 2025 - i)

export function fmt(value, digits = 2) {
  if (value === null || value === undefined) return '–'
  return typeof value === 'number' && !Number.isInteger(value) ? value.toFixed(digits) : String(value)
}

export function pct(value) {
  return value === null || value === undefined ? '–' : `${Number(value).toFixed(1)}%`
}
