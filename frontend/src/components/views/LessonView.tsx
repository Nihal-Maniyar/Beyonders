import React, { useState } from 'react'
import { Card } from '../common/Card'
import { Button } from '../common/Button'
import { Badge } from '../common/Badge'
import { Callout } from '../common/Callout'
import { FractionBar } from '../visuals/FractionBar'
import { FractionCompare } from '../visuals/FractionCompare'

export interface LessonViewProps {
  onProceedToPractice: () => void
}

export const LessonView: React.FC<LessonViewProps> = ({ onProceedToPractice }) => {
  const [activeTab, setActiveTab] = useState<'C1' | 'C2' | 'C3'>('C1')

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', margin: 0 }}>
            📚 Interactive Concept Lessons
          </h2>
          <p style={{ fontSize: '0.9rem', color: '#64748b', margin: '2px 0 0 0' }}>
            Master the core principles through visual worked examples and intuitive analogies.
          </p>
        </div>

        {/* Tab Buttons */}
        <div style={{ display: 'flex', gap: '8px', background: '#e2e8f0', padding: '4px', borderRadius: 'var(--radius-md)' }}>
          <Button
            size="sm"
            variant={activeTab === 'C1' ? 'primary' : 'ghost'}
            onClick={() => setActiveTab('C1')}
          >
            C1: Understanding
          </Button>
          <Button
            size="sm"
            variant={activeTab === 'C2' ? 'primary' : 'ghost'}
            onClick={() => setActiveTab('C2')}
          >
            C2: Comparing
          </Button>
          <Button
            size="sm"
            variant={activeTab === 'C3' ? 'primary' : 'ghost'}
            onClick={() => setActiveTab('C3')}
          >
            C3: Equivalence
          </Button>
        </div>
      </div>

      {/* TAB C1 */}
      {activeTab === 'C1' && (
        <Card
          title="Concept C1: What is a Fraction?"
          subtitle="Understanding numerator and denominator roles, and why equal-sized parts are mandatory."
          badge={<Badge variant="concept">Foundation</Badge>}
        >
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', margin: '16px 0' }}>
            <div style={{ background: '#f8fafc', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid #e2e8f0' }}>
              <h4 style={{ color: 'var(--color-numerator)', fontFamily: 'var(--font-display)', marginBottom: '6px' }}>
                Top: Numerator
              </h4>
              <p style={{ fontSize: '0.9rem', color: '#475569' }}>
                Answers <strong>"How many parts?"</strong>. Tells you the number of equal parts you have counted, shaded, or selected.
              </p>
            </div>
            <div style={{ background: '#f8fafc', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid #e2e8f0' }}>
              <h4 style={{ color: 'var(--color-denominator)', fontFamily: 'var(--font-display)', marginBottom: '6px' }}>
                Bottom: Denominator
              </h4>
              <p style={{ fontSize: '0.9rem', color: '#475569' }}>
                Answers <strong>"What size is each part?"</strong>. Tells you the total number of identical, equal parts that divide the whole unit.
              </p>
            </div>
          </div>

          <h4 style={{ fontFamily: 'var(--font-display)', marginTop: '20px' }}>
            Visual Example: 3/4 of a Strip
          </h4>
          <FractionBar
            numerator={3}
            denominator={4}
            label="4 equal parts make the whole; 3 are shaded"
            color="#2563eb"
          />

          <Callout type="misconception" title="Watch Out: Unequal Parts!">
            If a shape is cut into slices of <em>different sizes</em>, you cannot call one slice a unit fraction (like 1/3) because the parts are not fair shares! Fractions strictly require that every single partition is identical in area.
          </Callout>
        </Card>
      )}

      {/* TAB C2 */}
      {activeTab === 'C2' && (
        <Card
          title="Concept C2: Comparing Fractions with Different Denominators"
          subtitle="How to compare fractions when numerators match, denominators match, or both differ."
          badge={<Badge variant="warning">Core Goal</Badge>}
        >
          <div style={{ margin: '16px 0' }}>
            <p style={{ fontSize: '1rem', color: '#334155', lineHeight: 1.6 }}>
              When comparing fractions with the <strong>same numerator</strong> (e.g. 2/5 vs 2/3), students often fall into the whole-number trap: they think 5 is bigger than 3, so 2/5 must be bigger!
              <br />
              <strong>The Reality:</strong> Dividing the same whole into <em>more pieces</em> means each individual piece must be <em>smaller</em>!
            </p>
          </div>

          <FractionCompare
            title="The Denominator Size Effect: 2/5 vs 2/3"
            fractionA={{ numerator: 2, denominator: 5, label: '2 fifths (2/5) — whole cut into 5 parts' }}
            fractionB={{ numerator: 2, denominator: 3, label: '2 thirds (2/3) — whole cut into 3 parts' }}
          />

          <div style={{ background: '#f0fdf4', border: '1.5px solid #86efac', borderRadius: 'var(--radius-md)', padding: '16px', margin: '16px 0' }}>
            <h4 style={{ color: '#166534', fontFamily: 'var(--font-display)', marginBottom: '8px' }}>
              💡 Three Valid Comparison Methods:
            </h4>
            <ol style={{ paddingLeft: '20px', fontSize: '0.9rem', color: '#14532d', lineHeight: 1.6 }}>
              <li><strong>Equal Numerators:</strong> If top numbers match, the fraction with the <em>smaller denominator</em> has larger pieces and is greater (2/3 &gt; 2/5).</li>
              <li><strong>Equal Denominators:</strong> If bottom numbers match, parts are identical sizes, so more pieces wins (5/8 &gt; 3/8).</li>
              <li><strong>Common Denominators:</strong> When both differ (like 3/7 vs 4/9), find a common denominator (63): 3/7 = 27/63, while 4/9 = 28/63. Since 28 &gt; 27, 4/9 is larger!</li>
            </ol>
          </div>
        </Card>
      )}

      {/* TAB C3 */}
      {activeTab === 'C3' && (
        <Card
          title="Concept C3: Generating Equivalent Fractions"
          subtitle="Multiplicative scaling preserves proportion; addition destroys equivalence."
          badge={<Badge variant="success">Proportions</Badge>}
        >
          <p style={{ fontSize: '1rem', color: '#334155', lineHeight: 1.6, margin: '16px 0' }}>
            Equivalent fractions represent the <strong>exact same fraction of a whole</strong>, just sliced into more or fewer pieces.
            To keep them equivalent, you must multiply or divide both the numerator and denominator by the <em>same factor</em>.
          </p>

          <FractionCompare
            title="Visual Proof: 1/2 is Equivalent to 2/4"
            fractionA={{ numerator: 1, denominator: 2, label: '1 half (1/2)' }}
            fractionB={{ numerator: 2, denominator: 4, label: '2 fourths (2/4)' }}
          />

          <Callout type="misconception" title="Common Pitfall: Adding to Top and Bottom">
            <strong>Adding a number does NOT preserve equivalence!</strong>
            <br />
            For example, starting with 1/3 (~0.33) and adding 2 to top and bottom gives 3/5 (0.60). 3/5 is NOT equivalent to 1/3! Only multiplication and division keep the ratio unchanged.
          </Callout>
        </Card>
      )}

      {/* Navigation Footer */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '12px' }}>
        <Button variant="secondary" onClick={() => setActiveTab(activeTab === 'C3' ? 'C2' : 'C1')}>
          ⬅️ Previous Topic
        </Button>
        <Button size="lg" onClick={onProceedToPractice}>
          Proceed to Diagnostic Practice ➔
        </Button>
      </div>
    </div>
  )
}
