// Formatters are created once and reused. This is cleaner and cheaper than
// creating a new Intl formatter every time React renders metadata.
const numberFormatter = new Intl.NumberFormat('en')
const dateFormatter = new Intl.DateTimeFormat('en', {
  dateStyle: 'medium',
  timeStyle: 'short',
})

export const formatNumber = (value: number): string =>
  numberFormatter.format(value)

export const formatPercent = (value: number): string =>
  `${value.toFixed(value >= 10 ? 1 : 2)}%`

export const formatBytes = (value: number): string => {
  if (value === 0) {
    return '0 B'
  }

  const units = ['B', 'KB', 'MB', 'GB']
  const exponent = Math.min(
    Math.floor(Math.log(value) / Math.log(1024)),
    units.length - 1,
  )
  const amount = value / 1024 ** exponent

  return `${amount.toFixed(amount >= 10 || exponent === 0 ? 0 : 1)} ${units[exponent]}`
}

export const formatDateTime = (value: string): string => {
  const date = new Date(value)

  // Defensive fallback: if the backend ever sends a bad date string, the UI
  // still shows a readable value instead of "Invalid Date".
  if (Number.isNaN(date.getTime())) {
    return 'Unknown'
  }

  return dateFormatter.format(date)
}

export const formatBoolean = (value: boolean): string => (value ? 'Yes' : 'No')
