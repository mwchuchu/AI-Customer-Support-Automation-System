import styles from './Badge.module.css'

const colorMap = {
  // Status
  open:           'blue',
  in_progress:    'yellow',
  ai_resolved:    'green',
  human_resolved: 'green',
  escalated:      'orange',
  closed:         'gray',
  // Priority
  low:      'gray',
  medium:   'blue',
  high:     'yellow',
  critical: 'red',
  // Category / Sentiment
  positive:   'green',
  neutral:    'blue',
  negative:   'red',
  frustrated: 'orange',
  urgent:     'red',
}

export default function Badge({ label, variant }) {
  const color = variant || colorMap[label?.toLowerCase()] || 'gray'
  const display = label?.replace(/_/g, ' ') || '—'
  return (
    <span className={`${styles.badge} ${styles[color]}`}>
      {display}
    </span>
  )
}
