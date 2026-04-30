import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, Legend
} from 'recharts'
import { analyticsApi } from '../services/api'
import styles from './AnalyticsPage.module.css'

const COLORS = ['#00d4ff', '#00e676', '#ffc107', '#ff4444', '#9c6fff', '#ff6b35']

function Card({ title, children }) {
  return (
    <div className={styles.card}>
      <div className={styles.cardTitle}>{title}</div>
      {children}
    </div>
  )
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className={styles.tooltip}>
      {label && <div className={styles.tooltipLabel}>{label}</div>}
      {payload.map(p => (
        <div key={p.name} style={{ color: p.color || '#fff' }}>
          {p.name}: <strong>{p.value}</strong>
        </div>
      ))}
    </div>
  )
}

export default function AnalyticsPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    analyticsApi.summary()
      .then(r => setData(r.data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className={styles.page}>
      <div className={styles.loadingGrid}>
        {[1,2,3,4].map(i => <div key={i} className="skeleton" style={{height: 200, borderRadius: 12}} />)}
      </div>
    </div>
  )

  if (!data) return <div className={styles.page}><p>Failed to load analytics.</p></div>

  const categoryData = Object.entries(data.category_breakdown).map(([name, value]) => ({
    name: name.replace(/_/g, ' '), value
  }))
  const priorityData = Object.entries(data.priority_breakdown).map(([name, value]) => ({
    name, value
  }))
  const sentimentData = Object.entries(data.sentiment_breakdown).map(([name, value]) => ({
    name, value
  }))

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Analytics</h1>

      <div className={styles.statsRow}>
        {[
          { label: 'Total Tickets', value: data.total_tickets, color: 'accent' },
          { label: 'AI Resolved', value: data.ai_resolved, color: 'green' },
          { label: 'Escalated', value: data.escalated, color: 'orange' },
          { label: 'Auto-resolve Rate', value: `${data.auto_resolution_rate}%`, color: 'purple' },
          { label: 'Avg Confidence', value: `${(data.avg_confidence * 100).toFixed(0)}%`, color: 'yellow' },
        ].map(s => (
          <div key={s.label} className={styles.stat} style={{ '--c': `var(--${s.color})` }}>
            <div className={styles.statValue}>{s.value}</div>
            <div className={styles.statLabel}>{s.label}</div>
          </div>
        ))}
      </div>

      <div className={styles.chartsGrid}>
        {data.daily_volume.length > 0 && (
          <Card title="Daily Ticket Volume (7d)">
            <ResponsiveContainer width="100%" height={180}>
              <LineChart data={data.daily_volume}>
                <XAxis dataKey="date" tick={{ fill: '#8892a4', fontSize: 11 }} />
                <YAxis tick={{ fill: '#8892a4', fontSize: 11 }} />
                <Tooltip content={<CustomTooltip />} />
                <Line type="monotone" dataKey="count" stroke="#00d4ff" strokeWidth={2} dot={{ fill: '#00d4ff' }} name="Tickets" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        )}

        <Card title="By Category">
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={categoryData} layout="vertical">
              <XAxis type="number" tick={{ fill: '#8892a4', fontSize: 11 }} />
              <YAxis dataKey="name" type="category" tick={{ fill: '#8892a4', fontSize: 10 }} width={100} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" fill="#00d4ff" radius={[0, 4, 4, 0]} name="Count" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="By Priority">
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={priorityData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label={({ name, value }) => `${name}: ${value}`}>
                {priorityData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card title="By Sentiment">
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={sentimentData}>
              <XAxis dataKey="name" tick={{ fill: '#8892a4', fontSize: 11 }} />
              <YAxis tick={{ fill: '#8892a4', fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]} name="Count">
                {sentimentData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  )
}
