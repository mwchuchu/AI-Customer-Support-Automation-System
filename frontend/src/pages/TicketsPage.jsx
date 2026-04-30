import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Filter, Search, Clock, Bot } from 'lucide-react'
import { ticketsApi } from '../services/api'
import Badge from '../components/common/Badge'
import { formatDistanceToNow } from 'date-fns'
import styles from './TicketsPage.module.css'

export default function TicketsPage() {
  const [tickets, setTickets] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ status: '', priority: '', category: '' })
  const navigate = useNavigate()
  const PAGE_SIZE = 15

  const load = async () => {
    setLoading(true)
    try {
      const params = { page, page_size: PAGE_SIZE }
      if (filters.status)   params.status   = filters.status
      if (filters.priority) params.priority  = filters.priority
      if (filters.category) params.category  = filters.category
      const { data } = await ticketsApi.list(params)
      setTickets(data.tickets || [])
      setTotal(data.total || 0)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [page, filters])

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Tickets</h1>
          <p className={styles.sub}>{total} total tickets</p>
        </div>
        <button className={styles.newBtn} onClick={() => navigate('/tickets/new')}>
          <Plus size={16} /> New Ticket
        </button>
      </div>

      {/* Filters */}
      <div className={styles.filters}>
        <select value={filters.status} onChange={e => setFilters({...filters, status: e.target.value})}>
          <option value="">All Status</option>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="ai_resolved">AI Resolved</option>
          <option value="escalated">Escalated</option>
          <option value="human_resolved">Human Resolved</option>
          <option value="closed">Closed</option>
        </select>
        <select value={filters.priority} onChange={e => setFilters({...filters, priority: e.target.value})}>
          <option value="">All Priority</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select value={filters.category} onChange={e => setFilters({...filters, category: e.target.value})}>
          <option value="">All Categories</option>
          <option value="billing_inquiry">Billing</option>
          <option value="technical_issue">Technical</option>
          <option value="account_info">Account</option>
          <option value="complaint">Complaint</option>
          <option value="faq">FAQ</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div className={styles.table}>
        <div className={styles.tableHead}>
          <span>Ticket</span>
          <span>Subject</span>
          <span>Category</span>
          <span>Priority</span>
          <span>Status</span>
          <span>AI</span>
          <span>Created</span>
        </div>

        {loading ? (
          Array.from({length: 5}).map((_, i) => (
            <div key={i} className={`${styles.tableRow} skeleton`} style={{height: 52}} />
          ))
        ) : tickets.length === 0 ? (
          <div className={styles.empty}>No tickets found matching your filters.</div>
        ) : tickets.map(t => (
          <div key={t.id} className={styles.tableRow} onClick={() => navigate(`/tickets/${t.id}`)}>
            <span className={`${styles.mono} ${styles.num}`}>{t.ticket_number}</span>
            <span className={styles.subject}>{t.subject}</span>
            <span><Badge label={t.category} /></span>
            <span><Badge label={t.priority} /></span>
            <span><Badge label={t.status} /></span>
            <span>
              {t.auto_resolved
                ? <span className={styles.aiTag}><Bot size={11}/> AI</span>
                : <span className={styles.humanTag}>Human</span>
              }
            </span>
            <span className={styles.time}>
              <Clock size={11} />
              {formatDistanceToNow(new Date(t.created_at), { addSuffix: true })}
            </span>
          </div>
        ))}
      </div>

      {total > PAGE_SIZE && (
        <div className={styles.pagination}>
          <button disabled={page === 1} onClick={() => setPage(p => p - 1)}>← Prev</button>
          <span>Page {page} of {Math.ceil(total / PAGE_SIZE)}</span>
          <button disabled={page >= Math.ceil(total / PAGE_SIZE)} onClick={() => setPage(p => p + 1)}>Next →</button>
        </div>
      )}
    </div>
  )
}
