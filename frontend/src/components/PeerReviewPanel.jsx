import React from 'react';
import { Users, Star, Shield, MessageSquare } from 'lucide-react';

export default function PeerReviewPanel({ reviews }) {
    if (!reviews || reviews.length === 0) return null;

    // Group reviews by reviewed model
    const groupedByModel = {};
    reviews.forEach(r => {
        if (!groupedByModel[r.reviewed_model]) {
            groupedByModel[r.reviewed_model] = [];
        }
        groupedByModel[r.reviewed_model].push(r);
    });

    const getScoreColor = (score) => {
        if (score >= 8) return 'var(--brand-secondary)';
        if (score >= 6) return '#f59e0b';
        return 'var(--brand-danger)';
    };

    return (
        <div className="glass-panel animate-fade-in" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
            <h3 style={{
                fontSize: '1.1rem',
                margin: '0 0 1rem 0',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                color: 'var(--text-primary)'
            }}>
                <Users size={20} color="var(--brand-primary)" /> Peer Reviews
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                Each model reviewed the others' responses anonymously. Higher scores indicate better quality.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
                {Object.entries(groupedByModel).map(([model, modelReviews]) => {
                    const avgAccuracy = modelReviews.reduce((sum, r) => sum + r.accuracy_score, 0) / modelReviews.length;
                    const avgInsight = modelReviews.reduce((sum, r) => sum + r.insight_score, 0) / modelReviews.length;
                    const avgConstraint = modelReviews.reduce((sum, r) => sum + r.constraint_adherence, 0) / modelReviews.length;
                    const overallAvg = (avgAccuracy + avgInsight + avgConstraint) / 3;

                    return (
                        <div key={model} style={{
                            background: 'var(--bg-card)',
                            borderRadius: '10px',
                            padding: '1.25rem',
                            border: '1px solid var(--glass-border)'
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                <span style={{ fontWeight: 600, color: 'var(--brand-primary)' }}>{model}</span>
                                <span style={{
                                    background: getScoreColor(overallAvg),
                                    color: '#000',
                                    padding: '0.2rem 0.6rem',
                                    borderRadius: '6px',
                                    fontSize: '0.85rem',
                                    fontWeight: 600
                                }}>
                                    {overallAvg.toFixed(1)}/10
                                </span>
                            </div>

                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1rem' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                                    <span style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                                        <Star size={14} /> Accuracy
                                    </span>
                                    <span style={{ color: getScoreColor(avgAccuracy), fontWeight: 500 }}>{avgAccuracy.toFixed(1)}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                                    <span style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                                        <MessageSquare size={14} /> Insight
                                    </span>
                                    <span style={{ color: getScoreColor(avgInsight), fontWeight: 500 }}>{avgInsight.toFixed(1)}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                                    <span style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                                        <Shield size={14} /> Constraints
                                    </span>
                                    <span style={{ color: getScoreColor(avgConstraint), fontWeight: 500 }}>{avgConstraint.toFixed(1)}</span>
                                </div>
                            </div>

                            {modelReviews[0].feedback && (
                                <div style={{
                                    fontSize: '0.8rem',
                                    color: 'var(--text-secondary)',
                                    fontStyle: 'italic',
                                    borderTop: '1px solid var(--glass-border)',
                                    paddingTop: '0.75rem'
                                }}>
                                    "{modelReviews[0].feedback}"
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
