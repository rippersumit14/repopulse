// Formatters are created once and reused. This is cleaner and cheaper than
// creating a new Intl formatter every time React renders metadata.
const numberFormatter = new Intl.NumberFormat('en')
const dateFormatter = new Intl.DateTimeFormat('en', {
  dateStyle: 'medium',
  timeStyle: 'short',
})

export const formatNumber = (value: number): string =>
  numberFormatter.format(value)

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
