import React, { useState } from 'react'
import { Card } from '../common/Card'
import { Button } from '../common/Button'
import { Badge } from '../common/Badge'
import { Callout } from '../common/Callout'
import { VoicePlayer } from '../common/VoicePlayer'
import { VoiceInputButton } from '../common/VoiceInputButton'
import { TeachBackEvaluation, CriterionStatus } from '../../types'
import { api } from '../../services/api'

export interface TeachBackViewProps {
  learnerId: string
  sessionId?: string
  onProceedToPostAssessment: () => void
}

export const TeachBackView: React.FC<TeachBackViewProps> = ({
  learnerId,
  sessionId,
  onProceedToPostAssessment,
}) => {
  const [explanation, setExplanation] = useState('')
  const [evaluation, setEvaluation] = useState<TeachBackEvaluation | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async () => {
    if (!explanation.trim()) return

    setSubmitting(true)
    setError(null)
    try {
      const res = await api.evaluateTeachBack(learnerId, explanation, sessionId)
      setEvaluation(res)
    } catch (err: any) {
      setError(err.message || 'Failed to evaluate teach-back')
    } finally {
      setSubmitting(false)
    }
  }

  const getStatusBadge = (status: CriterionStatus) => {
    switch (status) {
      case 'demonstrated':
        return <Badge variant="success">Demonstrated (1.0 pt)</Badge>
      case 'partial':
        return <Badge variant="warning">Partial (0.5 pt)</Badge>
      case 'incorrect':
        return <Badge variant="misconception">Misconception (0.0 pt)</Badge>
      case 'not_demonstrated':
        return <Badge variant="neutral">Not Demonstrated (0.0 pt)</Badge>
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <Card
        title="🗣️ Student Teach-Back"
        subtitle="Explain what you learned in your own words. Teaching a concept is the ultimate proof of mastery!"
        badge={<Badge variant="brand">Rubric R1–R5</Badge>}
      >
        <p style={{ fontSize: '1rem', color: '#334155', lineHeight: 1.6, marginBottom: '16px' }}>
          Imagine you are teaching a friend who is confused about comparing fractions and equivalent fractions.
          In 3 to 5 sentences, explain:
        </p>

        <ul style={{ paddingLeft: '24px', fontSize: '0.9rem', color: '#475569', lineHeight: 1.6, marginBottom: '20px' }}>
          <li>What the <strong>numerator</strong> and <strong>denominator</strong> tell you.</li>
          <li>Why fraction pieces must always be <strong>equal in size</strong>.</li>
          <li>How having <strong>more pieces (larger denominator)</strong> affects the size of each piece.</li>
          <li>How to <strong>compare</strong> fractions (like 2/5 vs 2/3).</li>
          <li>How to generate <strong>equivalent fractions</strong>.</li>
        </ul>

        <div style={{ marginBottom: '20px' }}>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '10px',
              flexWrap: 'wrap',
              gap: '10px',
            }}
          >
            <label
              style={{
                fontFamily: 'var(--font-display)',
                fontWeight: 600,
                fontSize: '0.95rem',
                color: 'var(--color-text-primary)',
              }}
            >
              Your Explanation:
            </label>
            <VoiceInputButton
              label="🎙️ Speak Explanation"
              onTranscript={(text) => {
                setExplanation((prev) => (prev ? `${prev} ${text}` : text))
              }}
            />
          </div>
          <textarea
            rows={5}
            value={explanation}
            onChange={(e) => setExplanation(e.target.value)}
            placeholder="Write or speak your explanation here... (e.g. 'The denominator is the total number of equal parts...')"
            style={{
              width: '100%',
              fontFamily: 'var(--font-body)',
              fontSize: '1rem',
              padding: '14px',
              borderRadius: 'var(--radius-md)',
              border: '1.5px solid var(--color-border)',
              outline: 'none',
              resize: 'vertical',
              lineHeight: 1.5,
            }}
          />
        </div>

        {error && (
          <Callout type="misconception" title="Error">
            {error}
          </Callout>
        )}

        <Button
          size="lg"
          onClick={handleSubmit}
          disabled={!explanation.trim() || submitting}
          loading={submitting}
        >
          Submit Teach-Back for Rubric Evaluation ➔
        </Button>

        {/* Rubric Evaluation Results */}
        {evaluation && (
          <div style={{ marginTop: '28px', borderTop: '2px solid var(--color-border)', paddingTop: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
              <h4 style={{ fontFamily: 'var(--font-display)', fontSize: '1.25rem', margin: 0 }}>
                📊 Rubric Evaluation Scorecard
              </h4>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <Badge variant={evaluation.earned_points >= 3.5 ? 'success' : 'warning'}>
                  {evaluation.earned_points} / {evaluation.possible_points} Points ({evaluation.coverage_percent}%)
                </Badge>
              </div>
            </div>

            <VoicePlayer
              text={evaluation.overall_feedback}
              label="Listen to Evaluation Feedback"
            />

            <Callout
              type={evaluation.earned_points >= 3.5 ? 'success' : 'socratic'}
              title="Overall Rubric Feedback"
            >
              {evaluation.overall_feedback}
            </Callout>

            {/* Criteria Breakdown */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', margin: '20px 0' }}>
              {evaluation.criterion_results.map((cr) => (
                <div
                  key={cr.criterion_id}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: 'var(--radius-md)',
                    padding: '12px 16px',
                    gap: '12px',
                  }}
                >
                  <div>
                    <strong style={{ fontFamily: 'var(--font-display)', color: 'var(--color-text-primary)' }}>
                      Criterion {cr.criterion_id}:
                    </strong>{' '}
                    <span style={{ fontSize: '0.9rem', color: '#475569' }}>{cr.evidence}</span>
                  </div>
                  <div>{getStatusBadge(cr.status)}</div>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
              <Button size="lg" onClick={onProceedToPostAssessment}>
                Proceed to Final Post-Assessment 🏁
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  )
}
