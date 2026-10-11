import React, { useState } from 'react'
import { Card } from '../common/Card'
import { Button } from '../common/Button'
import { Badge } from '../common/Badge'
import { Callout } from '../common/Callout'
import { FractionCompare } from '../visuals/FractionCompare'
import { VoicePlayer } from '../common/VoicePlayer'
import { VoiceInputButton } from '../common/VoiceInputButton'
import { DiagnosisResult } from '../../types'
import { api } from '../../services/api'

export interface PracticeViewProps {
  learnerId: string
  sessionId?: string
  onGoToRemediation: (activityId: string) => void
  onProceedToTeachBack: () => void
}

export const PracticeView: React.FC<PracticeViewProps> = ({
  learnerId,
  sessionId,
  onGoToRemediation,
  onProceedToTeachBack,
}) => {
  const [selectedAnswer, setSelectedAnswer] = useState<string>('')
  const [reasoningText, setReasoningText] = useState<string>('')
  const [diagnosis, setDiagnosis] = useState<DiagnosisResult | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  const question = {
    question_id: 'Q_C2_PRE_01',
    concept_id: 'C2',
    question_text: 'Which fraction is larger: 2/5 or 2/3?',
    options: [
      'A) 2/5',
      'B) 2/3',
      'C) They are equal',
      'D) Cannot be determined without a calculator',
    ],
  }

  const handleSubmit = async () => {
    if (!selectedAnswer) return

    setLoading(true)
    setError(null)
    try {
      const choiceLetter = selectedAnswer.trim()[0].toUpperCase()
      const res = await api.diagnosePractice(
        learnerId,
        question.question_id,
        choiceLetter,
        reasoningText,
        sessionId
      )
      setDiagnosis(res)
    } catch (err: any) {
      setError(err.message || 'Failed to analyze reasoning')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <Card
        title="Interactive Diagnostic Practice"
        subtitle="Test your fraction comparison intuition. Explain your thinking so the tutor can investigate how you reason!"
        badge={<Badge variant="brand">Diagnostic Engine</Badge>}
      >
        <div
          style={{
            fontSize: '1.25rem',
            fontFamily: 'var(--font-display)',
            fontWeight: 700,
            color: 'var(--color-text-primary)',
            margin: '12px 0 20px 0',
          }}
        >
          {question.question_text}
        </div>

        {/* Options */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px', marginBottom: '20px' }}>
          {question.options.map((opt, idx) => {
            const isSelected = selectedAnswer === opt
            return (
              <label
                key={idx}
                onClick={() => setSelectedAnswer(opt)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 16px',
                  borderRadius: 'var(--radius-md)',
                  border: isSelected ? '2px solid var(--color-brand)' : '1.5px solid var(--color-border)',
                  backgroundColor: isSelected ? 'var(--color-brand-light)' : '#ffffff',
                  cursor: 'pointer',
                  fontWeight: isSelected ? 600 : 400,
                }}
              >
                <input
                  type="radio"
                  name="practice_choice"
                  checked={isSelected}
                  onChange={() => setSelectedAnswer(opt)}
                  style={{ accentColor: 'var(--color-brand)' }}
                />
                <span>{opt}</span>
              </label>
            )
          })}
        </div>

        {/* Reasoning explanation input */}
        <div style={{ marginBottom: '20px' }}>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '8px',
              flexWrap: 'wrap',
              gap: '8px',
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
              Explain your mathematical reasoning:
            </label>
            <VoiceInputButton
              label="🎙️ Speak Reasoning"
              onTranscript={(text) => {
                setReasoningText((prev) => (prev ? `${prev} ${text}` : text))
              }}
            />
          </div>
          <textarea
            rows={3}
            value={reasoningText}
            onChange={(e) => setReasoningText(e.target.value)}
            placeholder="Write or speak your reasoning... (e.g. 'I chose 2/3 because thirds are bigger pieces than fifths...' or 'I chose 2/5 because 5 is bigger than 3...')"
            style={{
              width: '100%',
              fontFamily: 'var(--font-body)',
              fontSize: '0.95rem',
              padding: '12px',
              borderRadius: 'var(--radius-md)',
              border: '1.5px solid var(--color-border)',
              outline: 'none',
              resize: 'vertical',
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
          disabled={!selectedAnswer || loading}
          loading={loading}
        >
          Diagnose My Reasoning ➔
        </Button>

        {/* Diagnosis Results */}
        {diagnosis && (
          <div style={{ marginTop: '28px', borderTop: '2px solid var(--color-border)', paddingTop: '20px' }}>
            <h4 style={{ fontFamily: 'var(--font-display)', fontSize: '1.2rem', marginBottom: '12px' }}>
              🧠 Diagnostic Assessment Result
            </h4>

            <VoicePlayer
              text={diagnosis.student_feedback + (diagnosis.clarifying_question ? ' ' + diagnosis.clarifying_question : '')}
              label="Listen to Tutor Feedback"
            />

            {diagnosis.is_correct ? (
              <Callout type="success" title="Correct Answer & Valid Thinking!">
                <p>{diagnosis.student_feedback}</p>
                <div style={{ marginTop: '10px', fontSize: '0.85rem', color: '#166534' }}>
                  <strong>Evidence:</strong> {diagnosis.evidence}
                </div>
              </Callout>
            ) : diagnosis.diagnosis_code === 'U1' ? (
              <Callout type="socratic" title="Tutor Clarification Needed">
                <p>{diagnosis.student_feedback}</p>
                {diagnosis.clarifying_question && (
                  <p style={{ marginTop: '8px', fontWeight: 600 }}>
                    💡 {diagnosis.clarifying_question}
                  </p>
                )}
              </Callout>
            ) : (
              <Callout type="misconception" title={`Misconception Diagnosed: [${diagnosis.diagnosis_code}]`}>
                <p style={{ fontSize: '1rem', lineHeight: 1.5 }}>{diagnosis.student_feedback}</p>
                <div style={{ marginTop: '10px', fontSize: '0.85rem' }}>
                  <strong>Diagnostic Code:</strong> {diagnosis.diagnosis_code} · <strong>Certainty:</strong> {diagnosis.certainty.toUpperCase()}
                </div>
                <div style={{ marginTop: '4px', fontSize: '0.85rem' }}>
                  <strong>Evidence:</strong> {diagnosis.evidence}
                </div>
              </Callout>
            )}

            {/* Visual Fraction Comparison */}
            <FractionCompare
              title="Visual Proof: 2/5 vs 2/3"
              fractionA={{ numerator: 2, denominator: 5, label: '2/5 (5 pieces per whole)' }}
              fractionB={{ numerator: 2, denominator: 3, label: '2/3 (3 pieces per whole)' }}
            />

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '20px' }}>
              {diagnosis.next_activity_id && (
                <Button
                  variant="primary"
                  onClick={() => onGoToRemediation(diagnosis.next_activity_id!)}
                >
                  Open Remediation Activity ({diagnosis.next_activity_id}) 🛠️
                </Button>
              )}
              <Button
                variant={diagnosis.next_activity_id ? 'secondary' : 'primary'}
                onClick={onProceedToTeachBack}
              >
                Proceed to Teach-Back 🗣️
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  )
}
