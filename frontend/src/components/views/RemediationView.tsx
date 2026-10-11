import React, { useState, useEffect } from 'react'
import { Card } from '../common/Card'
import { Button } from '../common/Button'
import { Badge } from '../common/Badge'
import { Callout } from '../common/Callout'
import { FractionCompare } from '../visuals/FractionCompare'
import { RemediationActivity } from '../../types'
import { api } from '../../services/api'

export interface RemediationViewProps {
  activityId: string
  onProceedToTeachBack: () => void
}

export const RemediationView: React.FC<RemediationViewProps> = ({
  activityId,
  onProceedToTeachBack,
}) => {
  const [activity, setActivity] = useState<RemediationActivity | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadActivity() {
      try {
        setLoading(true)
        const act = await api.getActivity(activityId)
        setActivity(act)
      } catch {
        // Fallback default activity
        setActivity({
          activity_id: activityId,
          concept_id: 'C2',
          title: 'Interactive Fraction Strips Explorer',
          purpose: 'Anchor part-size intuition through physical and visual fraction strip comparisons.',
          instructions: 'Look closely at the fraction strips below. Notice that each strip has the exact same total length (1 whole unit). When you divide the strip into more parts (like 5 parts), each individual piece becomes smaller.',
          expected_learning_evidence: 'Learner recognizes that dividing into more pieces decreases individual slice width.',
          target_diagnosis_codes: ['M1'],
          question_ids: ['Q_C2_PRE_01'],
        })
      } finally {
        setLoading(false)
      }
    }
    loadActivity()
  }, [activityId])

  if (loading) {
    return <Card title="Loading Remediation Activity...">Loading visual tools...</Card>
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <Card
        title={`🛠️ Remediation: ${activity?.title || activityId}`}
        subtitle={activity?.purpose}
        badge={<Badge variant="warning">{activity?.concept_id || 'Remedy'}</Badge>}
        accent="warning"
      >
        <div style={{ margin: '16px 0', fontSize: '1rem', color: '#334155', lineHeight: 1.6 }}>
          {activity?.instructions}
        </div>

        {/* Visual Fraction Strips Demo */}
        <FractionCompare
          title="Interactive Fraction Strip Comparison: 2/5 vs 2/3"
          fractionA={{ numerator: 2, denominator: 5, label: '2/5: 5 slices total (narrower pieces)' }}
          fractionB={{ numerator: 2, denominator: 3, label: '2/3: 3 slices total (wider pieces)' }}
        />

        <Callout type="teacher" title="Key Takeaway to Remember">
          {activity?.expected_learning_evidence ||
            'When denominators differ and numerators are equal, the fraction with fewer divisions has larger pieces!'}
        </Callout>

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
          <Button size="lg" onClick={onProceedToTeachBack}>
            I Understand! Proceed to Teach-Back ➔
          </Button>
        </div>
      </Card>
    </div>
  )
}
