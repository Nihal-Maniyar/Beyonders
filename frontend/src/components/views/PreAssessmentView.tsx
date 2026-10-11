import React, { useState, useEffect } from 'react'
import { Card } from '../common/Card'
import { Button } from '../common/Button'
import { Badge } from '../common/Badge'
import { Callout } from '../common/Callout'
import { Question } from '../../types'
import { api } from '../../services/api'

export interface PreAssessmentViewProps {
  learnerId: string
  sessionId?: string
  onComplete: () => void
}

export const PreAssessmentView: React.FC<PreAssessmentViewProps> = ({
  learnerId,
  sessionId,
  onComplete,
}) => {
  const [questions, setQuestions] = useState<Question[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [selectedOption, setSelectedOption] = useState<string>('')
  const [runId, setRunId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function initAssessment() {
      try {
        setLoading(true)
        const [qList, runData] = await Promise.all([
          api.getFixedAssessmentQuestions(),
          api.startAssessment(learnerId, 'pre', sessionId),
        ])
        setQuestions(qList)
        setRunId(runData.run_id)
      } catch (err: any) {
        setError(err.message || 'Failed to start baseline assessment')
      } finally {
        setLoading(false)
      }
    }
    initAssessment()
  }, [learnerId, sessionId])

  if (loading) {
    return (
      <Card title="Preparing Baseline Assessment...">
        <p style={{ color: '#64748b' }}>Loading approved questions bank...</p>
      </Card>
    )
  }

  if (error || questions.length === 0) {
    return (
      <Card title="Unable to Load Assessment" accent="misconception">
        <p style={{ color: 'var(--color-misconception)' }}>{error || 'No questions available'}</p>
        <Button variant="secondary" onClick={() => window.location.reload()}>
          Retry
        </Button>
      </Card>
    )
  }

  const currentQ = questions[currentIndex]
  const isLast = currentIndex === questions.length - 1

  const handleNext = async () => {
    if (!selectedOption || !runId) return

    setSubmitting(true)
    try {
      // Extract option letter (e.g. "A" from "A) ...")
      const choiceLetter = selectedOption.trim()[0].toUpperCase()
      await api.recordAssessmentAnswer(runId, currentQ.question_id, choiceLetter)

      if (isLast) {
        await api.completeAssessment(runId)
        onComplete()
      } else {
        setCurrentIndex((prev) => prev + 1)
        setSelectedOption('')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to record answer')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Progress Card */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#ffffff',
          padding: '12px 20px',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--color-border)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Badge variant="concept">Concept {currentQ.concept_id}</Badge>
          <span style={{ fontFamily: 'var(--font-display)', fontWeight: 600 }}>
            Question {currentIndex + 1} of {questions.length}
          </span>
        </div>

        {/* Progress meter */}
        <div style={{ width: '160px', height: '10px', backgroundColor: '#e2e8f0', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
          <div
            style={{
              width: `${((currentIndex + 1) / questions.length) * 100}%`,
              height: '100%',
              backgroundColor: 'var(--color-brand)',
              transition: 'width 200ms ease',
            }}
          />
        </div>
      </div>

      {/* Main Question Card */}
      <Card
        title={`Question ${currentIndex + 1}`}
        badge={<Badge variant="neutral">Baseline Check</Badge>}
      >
        <div
          style={{
            fontSize: '1.2rem',
            fontFamily: 'var(--font-display)',
            fontWeight: 600,
            color: 'var(--color-text-primary)',
            margin: '16px 0 24px 0',
            lineHeight: 1.5,
          }}
        >
          {currentQ.question_text}
        </div>

        {/* Options */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '24px' }}>
          {currentQ.options.map((opt, idx) => {
            const isSelected = selectedOption === opt
            return (
              <label
                key={idx}
                onClick={() => setSelectedOption(opt)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '14px',
                  padding: '14px 18px',
                  borderRadius: 'var(--radius-md)',
                  border: isSelected
                    ? '2px solid var(--color-brand)'
                    : '1.5px solid var(--color-border)',
                  backgroundColor: isSelected ? 'var(--color-brand-light)' : '#ffffff',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)',
                  fontFamily: 'var(--font-body)',
                  fontSize: '1rem',
                  color: isSelected ? 'var(--color-brand-active)' : 'var(--color-text-primary)',
                  fontWeight: isSelected ? 600 : 400,
                  boxShadow: isSelected ? '0 2px 4px rgba(37,99,235,0.08)' : 'none',
                }}
              >
                <input
                  type="radio"
                  name="pre_question_option"
                  checked={isSelected}
                  onChange={() => setSelectedOption(opt)}
                  style={{ accentColor: 'var(--color-brand)', transform: 'scale(1.2)' }}
                />
                <span>{opt}</span>
              </label>
            )
          })}
        </div>

        <Callout type="info" title="Assessment Confidentiality Notice">
          To provide an accurate initial baseline of your skills, answers and detailed explanations are kept confidential until after your post-assessment comparison.
        </Callout>

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
          <Button
            size="lg"
            onClick={handleNext}
            disabled={!selectedOption || submitting}
            loading={submitting}
          >
            {isLast ? 'Complete Baseline Check ➔' : 'Save & Next Question ➔'}
          </Button>
        </div>
      </Card>
    </div>
  )
}
