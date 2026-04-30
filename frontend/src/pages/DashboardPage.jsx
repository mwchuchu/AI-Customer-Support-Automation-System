import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Ticket, CheckCircle, AlertTriangle, Bot, TrendingUp, Clock } from 'lucide-react'
import { analyticsApi, ticketsApi } from '../services/api'
import { useAuthStore } from '../store/authStore'
import Badge from '../components/common/Badge'
import styles from './DashboardPage.module.css'
import { formatDistanceToNow } from 'date-fns'

function StatCard({ icon: Icon, label, value, color, sub }) {
  return (
    <div className={styles.statCard} style={{ '--card-color': `var(--${color})` }}>
      <div className={styles.statIcon}><Icon size={20} /></div>
      <div className={styles.statValue}>{value ?? '—'}</div>
      <div className={styles.statLabel}>{label}</div>
      {sub && <div className={styles.statSub}>{sub}</div>}
    </div>
  )
}

export default function DashboardPage() {
  const { user, isAgent } = useAuthStore()
  const [analytics, setAnalytics] = useState(null)
  const [recentTickets, setRecentTickets] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const load = async () => {
      try {
        const [ticketsRes] = await Promise.all([
          ticketsApi.list({ page: 1, page_size: 5 }),
        ])
        setRecentTickets(ticketsRes.data.tickets || [])

        if (isAgent()) {
          const analyticsRes = await analyticsApi.summary()
          setAnalytics(analyticsRes.data)
        }
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return (
    <div className={styles.page}>
      <div className={styles.pageHeader}>
        <div>
          <h1 className={styles.title}>
            Hello, <span>{user?.full_name?.split(' ')[0]}</span> 👋
          </h1>
          <p className={styles.subtitle}>
            {isAgent() ? 'Here\'s your support overview' : 'Track and manage your support tickets'}
          </p>
        </div>
      </div>

      {isAgent() && analytics && (
        <div className={styles.statsGrid}>
          <StatCard icon={Ticket}       label="Total Tickets"    value={analytics.total_tickets}   color="accent"  />
          <StatCard icon={Bot}          label="AI Resolved"      value={analytics.ai_resolved}     color="green"   sub={`${analytics.auto_resolution_rate}% auto-rate`} />
          <StatCard icon={AlertTriangle}label="Escalated"        value={analytics.escalated}       color="orange"  />
          <StatCard icon={TrendingUp}   label="Avg Confidence"   value={`${(analytics.avg_confidence * 100).toFixed(0)}%`} color="purple" />
        </div>
      )}

      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2>Recent Tickets</h2>
          <button className={styles.viewAll} onClick={() => navigate('/tickets')}>
            View all →
          </button>
        </div>

        {loading ? (
          <div className={styles.ticketList}>
            {[1,2,3].map(i => (
              <div key={i} className={`${styles.ticketRow} skeleton`} style={{ height: 64 }} />
            ))}
          </div>
        ) : recentTickets.length === 0 ? (
          <div className={styles.empty}>
            <Ticket size={32} />
            <p>No tickets yet. <button onClick={() => navigate('/tickets/new')}>Create one →</button></p>
          </div>
        ) : (
          <div className={styles.ticketList}>
            {recentTickets.map(t => (
              <div key={t.id} className={styles.ticketRow} onClick={() => navigate(`/tickets/${t.id}`)}>
                <div className={styles.ticketMain}>
                  <span className={`${styles.ticketNum} mono`}>{t.ticket_number}</span>
                  <span className={styles.ticketSubject}>{t.subject}</span>
                </div>
                <div className={styles.ticketMeta}>
                  <Badge label={t.status} />
                  <Badge label={t.priority} />
                  {t.auto_resolved && <Badge label="ai resolved" variant="green" />}
                  <span className={styles.ticketTime}>
                    <Clock size={12} />
                    {formatDistanceToNow(new Date(t.created_at), { addSuffix: true })}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
