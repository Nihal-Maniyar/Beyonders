"""Theme and design tokens for 'The Learning Notebook' UI."""

NOTEBOOK_CSS = """
<style>
/* Learning Notebook Design Tokens */
:root {
    --ink: #172A3A;
    --paper: #F7F4EC;
    --teal: #167D78;
    --amber: #D88A2D;
    --slate: #687782;
    --red: #B4473D;
    --light-teal: #E8F5F4;
    --light-amber: #FDF4E7;
    --border-color: #E2DDD3;
}

/* Base notebook feel */
.stApp {
    background-color: #FAFAF7;
    color: var(--ink);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Notebook Header Card */
.notebook-header {
    background: #FFFFFF;
    border: 1px solid var(--border-color);
    border-left: 5px solid var(--teal);
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.notebook-header h1 {
    color: var(--ink);
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0 0 0.5rem 0;
}

.notebook-header p {
    color: var(--slate);
    font-size: 0.95rem;
    margin: 0;
}

/* Callout cards */
.notebook-card {
    background: #FFFFFF;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.card-teal {
    background: var(--light-teal);
    border-color: #B5DFDC;
}

.card-amber {
    background: var(--light-amber);
    border-color: #F8D9A8;
}

/* Badge pills */
.badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

.badge-teal { background: #D1EBE9; color: #0C5552; }
.badge-amber { background: #FDE8CB; color: #8C5410; }
.badge-red { background: #FADBD8; color: #78281F; }
.badge-slate { background: #E5E8EB; color: #434F57; }

/* Fraction Strip Visual Container */
.fraction-strip-container {
    background: #FFFFFF;
    border: 1px dashed var(--border-color);
    border-radius: 6px;
    padding: 1rem;
    margin: 1rem 0;
}

.strip-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--slate);
    margin-bottom: 0.3rem;
}

.strip-bar {
    display: flex;
    height: 38px;
    border: 2px solid var(--ink);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.8rem;
}

.strip-segment {
    display: flex;
    align-items: center;
    justify-content: center;
    border-right: 1px solid var(--ink);
    font-size: 0.85rem;
    font-weight: 600;
}

.strip-segment:last-child {
    border-right: none;
}

.segment-shaded {
    background: var(--teal);
    color: #FFFFFF;
}

.segment-unshaded {
    background: #FFFFFF;
    color: var(--slate);
}

/* Rubric table row */
.rubric-row {
    border-bottom: 1px solid var(--border-color);
    padding: 0.75rem 0;
}
</style>
"""
