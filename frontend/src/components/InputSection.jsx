import React, { useState } from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';

export default function InputSection({ onRun, isLoading }) {
    const [prompt, setPrompt] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (prompt.trim() && !isLoading) {
            onRun(prompt);
        }
    };

    return (
        <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', marginBottom: '2rem' }}>
            <div style={{ marginBottom: '1.5rem' }}>
                <h1 style={{ fontSize: '2.5rem', fontWeight: 800, margin: '0 0 0.5rem 0', background: 'linear-gradient(135deg, #fff 0%, #94a1b2 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    Consensus Engine
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
                    Multi-LLM polling with traceable reasoning graphs.
                </p>
            </div>

            <form onSubmit={handleSubmit} style={{ maxWidth: '600px', margin: '0 auto' }}>
                <div style={{ position: 'relative' }}>
                    <textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Describe your complex or ambiguous request..."
                        style={{
                            width: '100%',
                            minHeight: '120px',
                            padding: '1rem',
                            borderRadius: '12px',
                            border: '1px solid var(--glass-border)',
                            background: 'rgba(0,0,0,0.2)',
                            color: 'var(--text-primary)',
                            fontSize: '1rem',
                            resize: 'vertical',
                            outline: 'none',
                            fontFamily: 'inherit'
                        }}
                    />
                    <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
                        <button
                            type="submit"
                            className="btn-primary"
                            disabled={isLoading || !prompt.trim()}
                            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                        >
                            {isLoading ? (
                                <>Processing...</>
                            ) : (
                                <>Analyze <ArrowRight size={18} /></>
                            )}
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
}
