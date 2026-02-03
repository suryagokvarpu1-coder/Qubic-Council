import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Database, Code, Layers, Activity, FileText, Eye } from 'lucide-react';

export default function NodeInspector({ graphState }) {
    const [activeTab, setActiveTab] = useState('responses');

    if (!graphState) return null;

    const tabs = [
        { id: 'responses', label: 'Model Responses', icon: <Eye size={14} /> },
        { id: 'claims', label: 'Claims (L4)', icon: <Activity size={14} /> },
        { id: 'agreement', label: 'Clusters (L5)', icon: <Layers size={14} /> },
        { id: 'raw', label: 'Raw State', icon: <Database size={14} /> },
    ];

    const renderContent = () => {
        switch (activeTab) {
            case 'responses':
                return (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
                        {graphState.model_responses?.map((res, idx) => (
                            <div key={idx} className="model-card" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                                <div style={{
                                    fontWeight: 'bold',
                                    marginBottom: '0.75rem',
                                    color: 'var(--brand-primary)',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center'
                                }}>
                                    <span>{res.model_id}</span>
                                    <span style={{
                                        fontSize: '0.75rem',
                                        color: 'var(--text-secondary)',
                                        fontWeight: 'normal'
                                    }}>
                                        {res.token_count} tokens
                                    </span>
                                </div>
                                <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                                    <ReactMarkdown>{res.response_text}</ReactMarkdown>
                                </div>
                            </div>
                        ))}
                    </div>
                );
            case 'claims':
                return (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
                        {graphState.all_claims?.map((res, idx) => (
                            <div key={idx} className="model-card">
                                <div style={{ fontWeight: 'bold', marginBottom: '0.75rem', color: 'var(--brand-primary)' }}>
                                    {res.model_id} ({res.claims.length} claims)
                                </div>
                                <ul style={{ margin: 0, paddingLeft: '1rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                    {res.claims.slice(0, 10).map((c, i) => (
                                        <li key={i} style={{ marginBottom: '0.5rem' }}>{c.text.slice(0, 150)}...</li>
                                    ))}
                                    {res.claims.length > 10 && (
                                        <li style={{ color: 'var(--brand-primary)', fontStyle: 'italic' }}>
                                            +{res.claims.length - 10} more claims
                                        </li>
                                    )}
                                </ul>
                            </div>
                        ))}
                    </div>
                );
            case 'agreement':
                return (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {graphState.scored_clusters?.map((cluster, idx) => (
                            <div key={idx} className="glass-panel" style={{ padding: '1rem' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                                    <div style={{ fontWeight: 600, fontSize: '1rem' }}>{cluster.canonical_claim}</div>
                                    <span style={{
                                        background: cluster.confidence_score >= 0.6 ? 'var(--brand-secondary)' : 'var(--brand-danger)',
                                        color: '#000',
                                        padding: '0.2rem 0.5rem',
                                        borderRadius: '4px',
                                        fontSize: '0.8rem',
                                        fontWeight: 600
                                    }}>
                                        {(cluster.confidence_score * 100).toFixed(0)}%
                                    </span>
                                </div>
                                <div style={{ display: 'flex', gap: '1rem', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
                                    <div style={{ color: 'var(--brand-secondary)' }}>
                                        ✓ {cluster.supporting_models.join(', ')}
                                    </div>
                                    {cluster.conflicting_models.length > 0 && (
                                        <div style={{ color: 'var(--brand-danger)' }}>
                                            ✗ {cluster.conflicting_models.join(', ')}
                                        </div>
                                    )}
                                </div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                                    {cluster.reasons.join(' • ')}
                                </div>
                            </div>
                        ))}
                    </div>
                );
            case 'raw':
                return (
                    <pre style={{
                        background: '#0d0d0f',
                        padding: '1rem',
                        borderRadius: '8px',
                        overflow: 'auto',
                        fontSize: '0.75rem',
                        maxHeight: '500px',
                        color: '#a6accd'
                    }}>
                        {JSON.stringify(graphState, null, 2)}
                    </pre>
                );
            default:
                return null;
        }
    };

    return (
        <div style={{ marginTop: '2rem' }}>
            <h3 style={{
                borderBottom: '1px solid var(--glass-border)',
                paddingBottom: '0.5rem',
                marginBottom: '1rem',
                color: 'var(--text-secondary)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
            }}>
                <Code size={18} /> Node Inspector
            </h3>

            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        style={{
                            background: activeTab === tab.id ? 'var(--bg-card)' : 'transparent',
                            border: activeTab === tab.id ? '1px solid var(--brand-primary)' : '1px solid transparent',
                            color: activeTab === tab.id ? 'var(--text-primary)' : 'var(--text-secondary)',
                            padding: '0.5rem 0.9rem',
                            borderRadius: '6px',
                            fontSize: '0.85rem',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.4rem',
                            transition: 'all 0.2s ease'
                        }}
                    >
                        {tab.icon} {tab.label}
                    </button>
                ))}
            </div>

            {renderContent()}
        </div>
    );
}
