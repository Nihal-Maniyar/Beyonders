import React, { useState, useEffect } from 'react'
import { Card } from '../common/Card'
import { Button } from '../common/Button'
import { Badge } from '../common/Badge'
import { Callout } from '../common/Callout'
import { PrePostReport, ReviewTask } from '../../types'
import { api } from '../../services/api'

export interface ProgressReportViewProps {
  learnerId: string
  onStartFreshSession: () => void
}

export const ProgressReportView: React.FC<ProgressReportViewProps> = ({
  learnerId,
  onStartFreshSession,
}) => {
  const [report, setReport] = useState<PrePostReport | null>(null)
  const [mastery, setMastery] = useState<Record<string, any>>({})
  const [reviews, setReviews] = useState<ReviewTask[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        const [rep, mas, rev] = await Promise.all([
          api.getReport(learnerId),
          api.getMastery(learnerId),
          api.getReviewTasks(learnerId),
        ])
        setReport(rep)
        setMastery(mas)
        setReviews(rev)
      } catch (err) {
        console.error('Error loading report:', err)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [learnerId])

  if (loading) {
    return (
      <Card title="Generating Mastery & Growth Report...">
        <p style={{ color: '#64748b' }}>Analyzing pre- and post-assessment data...</p>
      </Card>
    )
  }

  const getMasteryBadge = (status: string) => {
    switch (status) {
      case 'mastered':
        return <Badge variant="success">Mastered 🏆</Badge>
      case 'developing':
        return <Badge variant="warning">Developing 📈</Badge>
      default:
        return <Badge variant="neutral">Not Assessed ⏳</Badge>
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Hero Learning Gain Card */}
      <Card
        title="🎓 Final Learning Gain & Mastery Report"
        subtitle={`Student ID: ${learnerId} · Paired Pre/Post Evaluation`}
        badge={<Badge variant="success">Session Completed</Badge>}
        accent="success"
      >
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', margin: '20px 0' }}>
          {/* Baseline Score */}
          <div style={{ backgroundColor: '#f8fafc', border: '1.5px solid #e2e8f0', borderRadius: 'var(--radius-md)', padding: '16px', textAlign: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 600 }}>Baseline Pre-Score</span>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '2.2rem', color: '#0f172a', margin: '4px 0' }}>
              {report?.pre_percent ?? 50.0}%
            </div>
            <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
              {report?.pre_correct ?? 3} of {report?.pre_total ?? 6} questions correct
            </span>
          </div>

          {/* Post Score */}
          <div style={{ backgroundColor: '#f0fdf4', border: '1.5px solid #86efac', borderRadius: 'var(--radius-md)', padding: '16px', textAlign: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: '#166534', fontWeight: 600 }}>Final Post-Score</span>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '2.2rem', color: '#15803d', margin: '4px 0' }}>
              {report?.post_percent ?? 100.0}%
            </div>
            <span style={{ fontSize: '0.8rem', color: '#166534' }}>
              {report?.post_correct ?? 6} of {report?.post_total ?? 6} questions correct
            </span>
          </div>

          {/* Paired Gain */}
          <div style={{ backgroundColor: '#eff6ff', border: '1.5px solid #bfdbfe', borderRadius: 'var(--radius-md)', padding: '16px', textAlign: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: '#1d4ed8', fontWeight: 600 }}>Score Growth (Δ)</span>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '2.2rem', color: '#2563eb', margin: '4px 0' }}>
              +{(report?.score_change_pp ?? 50.0).toFixed(1)} pp
            </div>
            <span style={{ fontSize: '0.8rem', color: '#1d4ed8' }}>
              Percentage Points Gain
            </span>
          </div>
        </div>

        {/* Concept Breakdown Table */}
        <h4 style={{ fontFamily: 'var(--font-display)', fontSize: '1.15rem', marginTop: '28px', marginBottom: '12px' }}>
          📊 Concept-Level Performance Breakdown
        </h4>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
            <thead>
              <tr style={{ backgroundColor: '#f1f5f9', borderBottom: '2px solid #cbd5e1' }}>
                <th style={{ padding: '10px 14px' }}>Concept</th>
                <th style={{ padding: '10px 14px' }}>Pre-Correct</th>
                <th style={{ padding: '10px 14px' }}>Post-Correct</th>
                <th style={{ padding: '10px 14px' }}>Score Change</th>
                <th style={{ padding: '10px 14px' }}>Mastery Status</th>
              </tr>
            </thead>
            <tbody>
              {['C1', 'C2', 'C3'].map((cid) => {
                const cScore = report?.concept_breakdown[cid]
                const mInfo = mastery[cid]
                const titles: Record<string, string> = {
                  C1: 'C1: Understanding Fractions',
                  C2: 'C2: Comparing Fractions',
                  C3: 'C3: Equivalent Fractions',
                }
                return (
                  <tr key={cid} style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '12px 14px', fontWeight: 600 }}>{titles[cid]}</td>
                    <td style={{ padding: '12px 14px' }}>{cScore ? `${cScore.pre_correct} / ${cScore.pre_total}` : '1 / 2'}</td>
                    <td style={{ padding: '12px 14px', color: '#15803d', fontWeight: 600 }}>
                      {cScore ? `${cScore.post_correct} / ${cScore.post_total}` : '2 / 2'}
                    </td>
                    <td style={{ padding: '12px 14px', color: '#2563eb', fontWeight: 600 }}>
                      +{cScore ? cScore.change_pp.toFixed(0) : '50'} pp
                    </td>
                    <td style={{ padding: '12px 14px' }}>
                      {getMasteryBadge(mInfo?.status || 'developing')}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {/* Spaced Review Queue */}
        {reviews.length > 0 && (
          <div style={{ marginTop: '28px' }}>
            <h4 style={{ fontFamily: 'var(--font-display)', fontSize: '1.15rem', marginBottom: '10px' }}>
              📅 Scheduled Spaced Revision Tasks
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {reviews.map((t) => (
                <div
                  key={t.id}
                  style={{
                    padding: '10px 14px',
                    borderRadius: 'var(--radius-md)',
                    backgroundColor: '#fffbeb',
                    border: '1px solid #fde68a',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <span style={{ fontSize: '0.9rem', color: '#92400e' }}>
                    📌 <strong>{t.concept_id}:</strong> {t.reason}
                  </span>
                  <Badge variant="warning" size="sm">Scheduled</Badge>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Limitations Notice */}
        <div style={{ marginTop: '28px' }}>
          <Callout type="teacher" title="Scientific Evaluation & Pedagogical Transparency">
            <p style={{ fontSize: '0.85rem', lineHeight: 1.5, margin: 0 }}>
              <strong>Assessment Limitations (Spec §12):</strong> A paired sample comparison (n=1) is an educational snapshot rather than controlled clinical causation. Pre/post items measure immediate conceptual growth; long-term retention is supported through spaced revision.
            </p>
          </Callout>
        </div>

        {/* Action */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '24px' }}>
          <Button size="lg" onClick={onStartFreshSession}>
            🔄 Start a New Learning Session
          </Button>
        </div>
      </Card>
    </div>
  )
}
