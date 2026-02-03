import React from 'react';
import ReactMarkdown from 'react-markdown';
import { CheckCircle, AlertTriangle, Shield, Sparkles } from 'lucide-react';

export default function ConsensusView({ finalData }) {
    if (!finalData) return null;

    const { final_answer, confidence, uncertain_areas, reasoning_trace } = finalData;

    const getConfidenceColor = (score) => {
        if (score >= 0.7) return 'var(--brand-secondary)';
        if (score >= 0.5) return '#f59e0b';
        return 'var(--brand-danger)';
    };

    const getConfidenceLabel = (score) => {
        if (score >= 0.8) return 'High Confidence';
        if (score >= 0.6) return 'Moderate Confidence';
        if (score >= 0.4) return 'Low Confidence';
        return 'Very Low Confidence';
    };

    return (
        <div className="glass-panel animate-fade-in" style={{ padding: '2rem', marginBottom: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
                <h2 style={{ fontSize: '1.5rem', margin: 0, display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <Sparkles size={24} color="var(--brand-primary)" />
                    Council Consensus
                </h2>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div className="consensus-badge" style={{
                        background: getConfidenceColor(confidence),
                        color: '#000',
                        fontWeight: 600
                    }}>
                        {(confidence * 100).toFixed(0)}% {getConfidenceLabel(confidence)}
                    </div>
                </div>
            </div>

            <div style={{
                fontSize: '1.05rem',
                lineHeight: '1.7',
                marginBottom: '2rem',
                padding: '1.5rem',
                background: 'rgba(0,0,0,0.2)',
                borderRadius: '12px',
                border: '1px solid var(--glass-border)'
            }}>
                <ReactMarkdown>{final_answer}</ReactMarkdown>
            </div>

            {uncertain_areas && uncertain_areas.length > 0 && (
                <div style={{
                    background: 'rgba(239, 69, 101, 0.08)',
                    border: '1px solid rgba(239, 69, 101, 0.2)',
                    padding: '1rem 1.25rem',
                    borderRadius: '10px',
                    marginBottom: '1.5rem'
                }}>
                    <h3 style={{
                        fontSize: '0.95rem',
                        color: 'var(--brand-danger)',
                        margin: '0 0 0.75rem 0',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                    }}>
                        <AlertTriangle size={16} /> Disputed / Uncertain Areas
                    </h3>
                    <ul style={{ margin: 0, paddingLeft: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                        {uncertain_areas.map((area, idx) => (
                            <li key={idx} style={{ marginBottom: '0.25rem' }}>{area}</li>
                        ))}
                    </ul>
                </div>
            )}

            <div>
                <h3 style={{
                    fontSize: '0.85rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.08em',
                    color: 'var(--text-secondary)',
                    marginBottom: '0.75rem'
                }}>
                    Reasoning Trace
                </h3>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    {reasoning_trace && reasoning_trace.map((step, idx) => (
                        <div key={idx} style={{
                            padding: '0.5rem 0.85rem',
                            background: 'var(--bg-card)',
                            borderRadius: '8px',
                            fontSize: '0.8rem',
                            border: '1px solid var(--glass-border)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                        }}>
                            <div style={{
                                width: '6px',
                                height: '6px',
                                borderRadius: '50%',
                                background: 'var(--brand-primary)'
                            }}></div>
                            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{step.step}:</span>
                            <span style={{ color: 'var(--text-secondary)' }}>{step.details}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
