import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Send, Bot, Sparkles, AlertCircle } from 'lucide-react'
import { ticketsApi } from '../services/api'
import styles from './NewTicketPage.module.css'

export default function NewTicketPage() {
  const [form, setForm] = useState({ subject: '', description: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { data } = await ticketsApi.create(form)
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit ticket.')
    } finally {
      setLoading(false)
    }
  }

  if (result) {
    const aiLog = result.logs?.find(l => l.action === 'Auto-resolved by AI' || l.action === 'Escalated to human agent')
    const aiResponse = aiLog?.details?.response_text || aiLog?.details?.draft_response

    return (
      <div className={styles.page}>
        <div className={styles.resultCard}>
          <div className={`${styles.resultIcon} ${result.auto_resolved ? styles.resolved : styles.escalated}`}>
            {result.auto_resolved ? <Sparkles size={28} /> : <Bot size={28} />}
          </div>
          <h2 className={styles.resultTitle}>
            {result.auto_resolved ? 'Resolved by AI ✨' : 'Ticket Escalated'}
          </h2>
          <p className={styles.ticketNum}>{result.ticket_number}</p>

          {aiResponse && (
            <div className={styles.aiResponse}>
              <div className={styles.aiLabel}><Bot size={14} /> AI Response</div>
              <p>{aiResponse}</p>
            </div>
          )}

          <div className={styles.meta}>
            <span>Category: <strong>{result.category?.replace(/_/g, ' ')}</strong></span>
            <span>Priority: <strong>{result.priority}</strong></span>
            <span>Confidence: <strong>{(result.ai_confidence_score * 100).toFixed(0)}%</strong></span>
          </div>

          <div className={styles.actions}>
            <button className={styles.primaryBtn} onClick={() => navigate(`/tickets/${result.id}`)}>
              View Ticket
            </button>
            <button className={styles.ghostBtn} onClick={() => navigate('/tickets')}>
              All Tickets
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>New Support Ticket</h1>
        <p className={styles.subtitle}>
          Our AI processes your request instantly and either resolves it or routes it to the right agent.
        </p>
      </div>

      <div className={styles.formCard}>
        <div className={styles.aiBadge}>
          <Bot size={14} />
          <span>Powered by Gemini AI — instant classification & response</span>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {error && (
            <div className={styles.error}><AlertCircle size={14} /> {error}</div>
          )}

          <div className={styles.field}>
            <label>Subject <span>*</span></label>
            <input
              type="text"
              placeholder="Brief summary of your issue..."
              value={form.subject}
              onChange={(e) => setForm({ ...form, subject: e.target.value })}
              minLength={5}
              maxLength={500}
              required
            />
            <span className={styles.charCount}>{form.subject.length}/500</span>
          </div>

          <div className={styles.field}>
            <label>Description <span>*</span></label>
            <textarea
              placeholder="Describe your issue in detail. Include any relevant information such as error messages, steps to reproduce, or account details..."
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              minLength={10}
              rows={8}
              required
            />
          </div>

          <button type="submit" className={styles.submit} disabled={loading}>
            {loading ? (
              <>
                <span className={styles.spinner} />
                AI is processing...
              </>
            ) : (
              <>
                <Send size={16} />
                Submit Ticket
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
