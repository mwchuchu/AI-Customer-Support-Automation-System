import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Bot, User, Clock, Cpu, AlertTriangle, CheckCircle, Activity } from 'lucide-react'
import { ticketsApi, agentsApi } from '../services/api'
import { useAuthStore } from '../store/authStore'
import Badge from '../components/common/Badge'
import { formatDistanceToNow, format } from 'date-fns'
import styles from './TicketDetailPage.module.css'

export default function TicketDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { isAgent } = useAuthStore()
  const [ticket, setTicket] = useState(null)
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)

  useEffect(() => {
    const load = async () => {
      try {
        const [ticketRes] = await Promise.all([ticketsApi.get(id)])
        setTicket(ticketRes.data)
        if (isAgent()) {
          const agentsRes = await agentsApi.list()
          setAgents(agentsRes.data)
        }
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  const updateTicket = async (updates) => {
    setUpdating(true)
    try {
      const { data } = await ticketsApi.update(id, updates)
      setTicket(data)
    } finally {
      setUpdating(false)
    }
  }

  if (loading) return <div className={styles.loading}><span className={styles.spinner} /></div>
  if (!ticket) return <div className={styles.page}><p>Ticket not found.</p></div>

  const aiGenerateLog = ticket.logs?.find(l => l.action === 'Auto-resolved by AI' || l.action === 'Escalated to human agent')
  const aiResponseText = aiGenerateLog?.details?.response_text || aiGenerateLog?.details?.draft_response

  return (
    <div className={styles.page}>
      <button className={styles.back} onClick={() => navigate('/tickets')}>
        <ArrowLeft size={16} /> Back to tickets
      </button>

      <div className={styles.topRow}>
        <div>
          <span className={`${styles.ticketNum} mono`}>{ticket.ticket_number}</span>
          <h1 className={styles.subject}>{ticket.subject}</h1>
          <div className={styles.badges}>
            <Badge label={ticket.status} />
            <Badge label={ticket.priority} />
            <Badge label={ticket.category} />
            <Badge label={ticket.sentiment} />
            {ticket.auto_resolved && <Badge label="ai resolved" variant="green" />}
          </div>
        </div>

        {isAgent() && (
          <div className={styles.agentControls}>
            <select
              value={ticket.status}
              onChange={e => updateTicket({ status: e.target.value })}
              disabled={updating}
            >
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="escalated">Escalated</option>
              <option value="human_resolved">Human Resolved</option>
              <option value="closed">Closed</option>
            </select>
            <select
              value={ticket.assigned_agent_id || ''}
              onChange={e => updateTicket({ assigned_agent_id: e.target.value || null })}
              disabled={updating}
            >
              <option value="">Unassigned</option>
              {agents.map(a => <option key={a.id} value={a.id}>{a.full_name}</option>)}
            </select>
          </div>
        )}
      </div>

      <div className={styles.grid}>
        {/* Left column */}
        <div className={styles.left}>
          {/* Description */}
          <div className={styles.card}>
            <div className={styles.cardTitle}><User size={14} /> Customer Message</div>
            <p className={styles.description}>{ticket.description}</p>
          </div>

          {/* AI Response */}
          {aiResponseText && (
            <div className={`${styles.card} ${styles.aiCard}`}>
              <div className={styles.cardTitle}><Bot size={14} /> AI Response</div>
              <p className={styles.description}>{aiResponseText}</p>
              {aiGenerateLog?.details?.resolution_steps?.length > 0 && (
                <div className={styles.steps}>
                  <strong>Resolution Steps:</strong>
                  <ol>
                    {aiGenerateLog.details.resolution_steps.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ol>
                </div>
              )}
            </div>
          )}

          {/* AI Pipeline Metrics */}
          {ticket.ai_responses?.length > 0 && (
            <div className={styles.card}>
              <div className={styles.cardTitle}><Cpu size={14} /> AI Pipeline Steps</div>
              <div className={styles.pipelineSteps}>
                {ticket.ai_responses.map((r, i) => (
                  <div key={r.id} className={`${styles.step} ${r.success ? styles.stepOk : styles.stepFail}`}>
                    <div className={styles.stepNum}>{i + 1}</div>
                    <div className={styles.stepContent}>
                      <div className={styles.stepName}>{r.pipeline_step.replace(/_/g, ' ')}</div>
                      <div className={styles.stepMeta}>
                        <span>Confidence: <strong>{(r.confidence_score * 100).toFixed(0)}%</strong></span>
                        <span>{r.latency_ms}ms</span>
                        <span>{r.tokens_used} tokens</span>
                      </div>
                    </div>
                    {r.success
                      ? <CheckCircle size={14} className={styles.stepOkIcon} />
                      : <AlertTriangle size={14} className={styles.stepFailIcon} />
                    }
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right column */}
        <div className={styles.right}>
          {/* Details */}
          <div className={styles.card}>
            <div className={styles.cardTitle}><Activity size={14} /> Details</div>
            <div className={styles.detailRows}>
              <div className={styles.detailRow}>
                <span>Customer</span>
                <strong>{ticket.customer?.full_name}</strong>
              </div>
              <div className={styles.detailRow}>
                <span>Assigned To</span>
                <strong>{ticket.assigned_agent?.full_name || '—'}</strong>
              </div>
              <div className={styles.detailRow}>
                <span>Confidence</span>
                <strong>{(ticket.ai_confidence_score * 100).toFixed(0)}%</strong>
              </div>
              <div className={styles.detailRow}>
                <span>Created</span>
                <strong>{format(new Date(ticket.created_at), 'MMM d, HH:mm')}</strong>
              </div>
              {ticket.resolved_at && (
                <div className={styles.detailRow}>
                  <span>Resolved</span>
                  <strong>{format(new Date(ticket.resolved_at), 'MMM d, HH:mm')}</strong>
                </div>
              )}
            </div>
            {ticket.ai_summary && (
              <div className={styles.summary}>
                <div className={styles.summaryLabel}>AI Summary</div>
                <p>{ticket.ai_summary}</p>
              </div>
            )}
            {ticket.suggested_tags?.length > 0 && (
              <div className={styles.tags}>
                {ticket.suggested_tags.map(t => (
                  <span key={t} className={styles.tag}>{t}</span>
                ))}
              </div>
            )}
          </div>

          {/* Audit Log */}
          <div className={styles.card}>
            <div className={styles.cardTitle}><Clock size={14} /> Audit Log</div>
            <div className={styles.logs}>
              {ticket.logs?.slice().reverse().map(log => (
                <div key={log.id} className={styles.logRow}>
                  <div className={`${styles.logDot} ${log.actor === 'ai' ? styles.aiDot : ''}`} />
                  <div>
                    <div className={styles.logAction}>{log.action}</div>
                    <div className={styles.logMeta}>
                      {log.actor} · {formatDistanceToNow(new Date(log.created_at), { addSuffix: true })}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
