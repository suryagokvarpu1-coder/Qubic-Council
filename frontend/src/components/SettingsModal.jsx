import React, { useState, useEffect } from 'react';
import { X, Key, Save, Check, AlertCircle, Loader2 } from 'lucide-react';
import axios from 'axios';

const API_URL = "http://localhost:8000";

export default function SettingsModal({ onClose }) {
    const [openrouterKey, setOpenrouterKey] = useState('');
    const [groqKey, setGroqKey] = useState('');
    const [status, setStatus] = useState('');
    const [statusType, setStatusType] = useState('info'); // info, success, error
    const [saved, setSaved] = useState(false);
    const [loading, setLoading] = useState(false);
    const [providerStatus, setProviderStatus] = useState({
        openrouter: { configured: false },
        groq: { configured: false }
    });

    // Fetch current provider status on mount
    useEffect(() => {
        fetchProviderStatus();
    }, []);

    const fetchProviderStatus = async () => {
        try {
            const res = await axios.get(`${API_URL}/settings/keys/status`);
            setProviderStatus(res.data.providers || {});
        } catch (e) {
            console.error('Failed to fetch provider status:', e);
        }
    };

    const handleSave = async () => {
        // Validate at least one key is provided
        if (!openrouterKey.trim() && !groqKey.trim()) {
            setStatus('Please enter at least one API key');
            setStatusType('error');
            return;
        }

        setLoading(true);
        setStatus('');

        try {
            const payload = {};
            if (openrouterKey.trim()) payload.openrouter_api_key = openrouterKey.trim();
            if (groqKey.trim()) payload.groq_api_key = groqKey.trim();

            const res = await axios.post(`${API_URL}/settings/keys`, payload);

            const providers = res.data.available_providers || [];
            const providerNames = providers.map(p => p.charAt(0).toUpperCase() + p.slice(1)).join(' + ');

            setSaved(true);
            setStatus(providers.length > 0 ? `Connected: ${providerNames}` : 'Keys saved successfully!');
            setStatusType('success');

            // Clear inputs for security
            if (openrouterKey.trim()) setOpenrouterKey('');
            if (groqKey.trim()) setGroqKey('');

            // Update provider status
            if (res.data.providers_status) {
                setProviderStatus(res.data.providers_status);
            }

            setTimeout(() => {
                setSaved(false);
                onClose();
            }, 1500);
        } catch (e) {
            setStatus('Failed to save API keys. Please try again.');
            setStatusType('error');
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (type) => {
        switch (type) {
            case 'success': return 'var(--brand-secondary)';
            case 'error': return 'var(--brand-danger)';
            default: return 'var(--text-secondary)';
        }
    };

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
            background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(5px)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 1000
        }}>
            <div className="glass-panel" style={{ width: '500px', padding: '2rem', position: 'relative' }}>
                <button onClick={onClose} style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                    <X size={20} />
                </button>

                <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: 0 }}>
                    <Key size={20} color="var(--brand-primary)" /> API Configuration
                </h2>

                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                    Configure your LLM provider API keys. You can use one or both providers for maximum flexibility.
                </p>

                {/* OpenRouter Key */}
                <div style={{ marginBottom: '1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <label style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.3rem',
                            fontSize: '0.85rem',
                            fontWeight: 600,
                            color: 'var(--text-primary)'
                        }}>
                            <Key size={14} /> OpenRouter API Key
                        </label>
                        <span style={{
                            fontSize: '0.7rem',
                            padding: '0.2rem 0.5rem',
                            borderRadius: '4px',
                            background: providerStatus.openrouter?.configured ? 'rgba(74, 222, 128, 0.2)' : 'rgba(255, 255, 255, 0.1)',
                            color: providerStatus.openrouter?.configured ? '#4ade80' : 'var(--text-secondary)'
                        }}>
                            {providerStatus.openrouter?.configured ? '✓ Connected' : 'Not configured'}
                        </span>
                    </div>
                    <input
                        type="password"
                        value={openrouterKey}
                        onChange={(e) => setOpenrouterKey(e.target.value)}
                        placeholder={providerStatus.openrouter?.configured ? "Key saved (enter new to replace)" : "sk-or-v1-..."}
                        style={{
                            width: '100%',
                            padding: '0.75rem',
                            background: 'var(--bg-card)',
                            border: '1px solid var(--glass-border)',
                            borderRadius: '8px',
                            color: 'var(--text-primary)',
                            fontSize: '0.9rem',
                            fontFamily: 'monospace',
                            outline: 'none'
                        }}
                    />
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                        Access GPT-4o, Claude, Gemini & more. Get key at{' '}
                        <a href="https://openrouter.ai/keys" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--brand-primary)', textDecoration: 'none' }}>openrouter.ai/keys</a>
                    </div>
                </div>

                {/* Groq Key */}
                <div style={{ marginBottom: '1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <label style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.3rem',
                            fontSize: '0.85rem',
                            fontWeight: 600,
                            color: 'var(--text-primary)'
                        }}>
                            <Key size={14} /> Groq API Key
                        </label>
                        <span style={{
                            fontSize: '0.7rem',
                            padding: '0.2rem 0.5rem',
                            borderRadius: '4px',
                            background: providerStatus.groq?.configured ? 'rgba(74, 222, 128, 0.2)' : 'rgba(255, 255, 255, 0.1)',
                            color: providerStatus.groq?.configured ? '#4ade80' : 'var(--text-secondary)'
                        }}>
                            {providerStatus.groq?.configured ? '✓ Connected' : 'Not configured'}
                        </span>
                    </div>
                    <input
                        type="password"
                        value={groqKey}
                        onChange={(e) => setGroqKey(e.target.value)}
                        placeholder={providerStatus.groq?.configured ? "Key saved (enter new to replace)" : "gsk_..."}
                        style={{
                            width: '100%',
                            padding: '0.75rem',
                            background: 'var(--bg-card)',
                            border: '1px solid var(--glass-border)',
                            borderRadius: '8px',
                            color: 'var(--text-primary)',
                            fontSize: '0.9rem',
                            fontFamily: 'monospace',
                            outline: 'none'
                        }}
                    />
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                        Ultra-fast Llama inference. Get key at{' '}
                        <a href="https://console.groq.com/keys" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--brand-primary)', textDecoration: 'none' }}>console.groq.com/keys</a>
                    </div>
                </div>

                {status && (
                    <div style={{
                        marginBottom: '1rem',
                        padding: '0.75rem',
                        borderRadius: '8px',
                        background: statusType === 'error' ? 'rgba(239, 69, 101, 0.1)' : 'rgba(74, 222, 128, 0.1)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        fontSize: '0.9rem',
                        color: getStatusColor(statusType)
                    }}>
                        {statusType === 'error' ? <AlertCircle size={16} /> : <Check size={16} />}
                        {status}
                    </div>
                )}

                <button
                    onClick={handleSave}
                    className="btn-primary"
                    disabled={loading}
                    style={{ 
                        width: '100%', 
                        display: 'flex', 
                        justifyContent: 'center', 
                        alignItems: 'center', 
                        gap: '0.5rem',
                        opacity: loading ? 0.7 : 1
                    }}
                >
                    {loading ? (
                        <>
                            <Loader2 size={18} className="animate-spin" /> Saving...
                        </>
                    ) : saved ? (
                        <>
                            <Check size={18} /> Saved!
                        </>
                    ) : (
                        <>
                            <Save size={18} /> Save API Keys
                        </>
                    )}
                </button>

                <p style={{ 
                    fontSize: '0.75rem', 
                    color: 'var(--text-secondary)', 
                    marginTop: '1rem',
                    textAlign: 'center',
                    opacity: 0.7
                }}>
                    🔒 Keys are stored in memory only and never logged
                </p>
            </div>
        </div>
    );
}
