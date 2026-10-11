import React from 'react'
import { ConceptMastery, PrePostReport, ReviewTask } from '../../types'
import { Badge } from '../common/Badge'

export interface RightInfoPanelProps {
  studentName: string
  learnerId: string
  masteries: Record<string, ConceptMastery>
  report: PrePostReport | null
  reviews: ReviewTask[]
  onNavigateToStage: (tabId: string) => void
}

export const RightInfoPanel: React.FC<RightInfoPanelProps> = ({
  studentName,
  learnerId,
  masteries,
  report,
  reviews,
  onNavigateToStage,
}) => {
  const getStatusBadge = (status?: string) => {
    switch (status) {
      case 'mastered':
        return <Badge variant="success" size="sm">Mastered 🏆</Badge>
      case 'developing':
        return <Badge variant="warning" size="sm">Developing 📈</Badge>
      default:
        return <Badge variant="neutral" size="sm">Not Assessed ⏳</Badge>
    }
  }

  const concepts = [
    { id: 'C1', title: 'Understanding Fractions', color: '#0284c7' },
    { id: 'C2', title: 'Comparing Fractions', color: '#ff6f43' },
    { id: 'C3', title: 'Equivalent Fractions', color: '#059669' },
  ]

  return (
    <aside
      style={{
        width: '320px',
        flexShrink: 0,
        backgroundColor: '#ffffff',
        borderLeft: '1.5px solid var(--color-border)',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
        padding: '24px 20px',
        minHeight: 'calc(100vh - 72px)',
        overflowY: 'auto',
      }}
    >
      {/* Student Profile Card */}
      <div
        style={{
          background: 'linear-gradient(135deg, #fff2ed 0%, #ffffff 100%)',
          border: '1.5px solid var(--color-brand-border)',
          borderRadius: 'var(--radius-lg)',
          padding: '18px',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '12px' }}>
          <div
            style={{
              width: '46px',
              height: '46px',
              borderRadius: '50%',
              backgroundColor: 'var(--color-brand)',
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.3rem',
              fontWeight: 700,
              boxShadow: 'var(--shadow-tactile)',
            }}
          >
            {studentName.charAt(0).toUpperCase() || 'S'}
          </div>
          <div>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.1rem', color: 'var(--color-text-primary)' }}>
              {studentName}
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
              ID: {learnerId}
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.72rem', padding: '3px 8px', borderRadius: 'var(--radius-full)', backgroundColor: '#ffffff', border: '1px solid var(--color-border)', color: 'var(--color-text-secondary)', fontWeight: 600 }}>
            Visual Learner
          </span>
          <span style={{ fontSize: '0.72rem', padding: '3px 8px', borderRadius: 'var(--radius-full)', backgroundColor: '#ffffff', border: '1px solid var(--color-border)', color: 'var(--color-text-secondary)', fontWeight: 600 }}>
            Grade 4–6
          </span>
          <span style={{ fontSize: '0.72rem', padding: '3px 8px', borderRadius: 'var(--radius-full)', backgroundColor: '#ffffff', border: '1px solid var(--color-border)', color: 'var(--color-text-secondary)', fontWeight: 600 }}>
            Self-Paced
          </span>
        </div>
      </div>

      {/* Real-Time Concept Mastery Card */}
      <div
        style={{
          backgroundColor: '#ffffff',
          border: '1.5px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          padding: '18px',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <h4 style={{ fontFamily: 'var(--font-display)', fontSize: '0.98rem', margin: 0, color: 'var(--color-text-primary)' }}>
            Concept Mastery
          </h4>
          <button
            onClick={() => onNavigateToStage('progress')}
            style={{ fontSize: '0.75rem', color: 'var(--color-brand)', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600 }}
          >
            Full Report ➔
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {concepts.map((c) => {
            const mastery = masteries[c.id]
            const status = mastery?.status || 'not_assessed'
            const scorePercent = Math.round((mastery?.score || 0) * 100)
            const attempts = mastery?.evidence_attempt_count || 0

            return (
              <div
                key={c.id}
                style={{
                  padding: '10px 12px',
                  backgroundColor: 'var(--color-canvas)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-md)',
                  borderLeft: `4px solid ${c.color}`,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--color-text-primary)' }}>
                    {c.id}: {c.title}
                  </span>
                  {getStatusBadge(status)}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '4px' }}>
                  <span>{attempts} evidence {attempts === 1 ? 'attempt' : 'attempts'}</span>
                  <span>{scorePercent}% score</span>
                </div>
                {/* Progress bar */}
                <div style={{ width: '100%', height: '5px', backgroundColor: '#e2e8f0', borderRadius: '3px', marginTop: '6px', overflow: 'hidden' }}>
                  <div
                    style={{
                      width: `${scorePercent}%`,
                      height: '100%',
                      backgroundColor: status === 'mastered' ? 'var(--color-success)' : status === 'developing' ? 'var(--color-warning)' : '#94a3b8',
                      transition: 'width 300ms ease',
                    }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Pre vs Post Assessment Card */}
      <div
        style={{
          backgroundColor: '#ffffff',
          border: '1.5px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          padding: '18px',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <h4 style={{ fontFamily: 'var(--font-display)', fontSize: '0.98rem', margin: 0, color: 'var(--color-text-primary)' }}>
            Assessment Scorecard
          </h4>
          <Badge variant="brand" size="sm">Paired Check</Badge>
        </div>

        {report ? (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
              <div style={{ backgroundColor: '#f8fafc', padding: '10px', borderRadius: 'var(--radius-sm)', textAlign: 'center', border: '1px solid var(--color-border)' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Pre-Test</div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-text-primary)' }}>
                  {report.pre_correct}/{report.pre_total}
                </div>
                <div style={{ fontSize: '0.72rem', color: '#64748b' }}>({report.pre_percent.toFixed(0)}%)</div>
              </div>
              <div style={{ backgroundColor: '#f0fdf4', padding: '10px', borderRadius: 'var(--radius-sm)', textAlign: 'center', border: '1px solid #bbf7d0' }}>
                <div style={{ fontSize: '0.75rem', color: '#166534' }}>Post-Test</div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.25rem', fontWeight: 700, color: '#166534' }}>
                  {report.post_correct}/{report.post_total}
                </div>
                <div style={{ fontSize: '0.72rem', color: '#15803d' }}>({report.post_percent.toFixed(0)}%)</div>
              </div>
            </div>

            <div style={{ textAlign: 'center', padding: '8px', backgroundColor: report.score_change_pp >= 0 ? '#ecfdf5' : '#fff1f2', borderRadius: 'var(--radius-sm)', border: `1px solid ${report.score_change_pp >= 0 ? '#a7f3d0' : '#fecdd3'}` }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: report.score_change_pp >= 0 ? '#047857' : '#be123c' }}>
                Observed Growth: {report.score_change_pp > 0 ? `+${report.score_change_pp.toFixed(1)}` : report.score_change_pp.toFixed(1)} pp
              </span>
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '16px 8px', color: 'var(--color-text-muted)', fontSize: '0.82rem' }}>
            <span>Complete Pre- and Post-assessments to view paired score comparison.</span>
          </div>
        )}
      </div>

      {/* Scheduled Review Queue Card */}
      {reviews.length > 0 && (
        <div
          style={{
            backgroundColor: '#fffdf5',
            border: '1.5px solid #fef08a',
            borderRadius: 'var(--radius-lg)',
            padding: '16px',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.1rem' }}>📌</span>
            <h4 style={{ fontFamily: 'var(--font-display)', fontSize: '0.92rem', margin: 0, color: '#854d0e' }}>
              Spaced Review Queue ({reviews.length})
            </h4>
          </div>
          <p style={{ fontSize: '0.78rem', color: '#a16207', margin: '0 0 10px 0', lineHeight: 1.4 }}>
            Scheduled automatically from detected misconceptions:
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {reviews.map((task) => (
              <div
                key={task.id}
                style={{
                  padding: '6px 10px',
                  backgroundColor: '#ffffff',
                  border: '1px solid #fde047',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.78rem',
                  color: '#713f12',
                }}
              >
                <strong>{task.concept_id}:</strong> {task.reason}
              </div>
            ))}
          </div>
        </div>
      )}
    </aside>
  )
}
