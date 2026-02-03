import React, { useState } from 'react';
import { X, Key, Save, Check } from 'lucide-react';
import axios from 'axios';

const API_URL = "http://localhost:8000";

export default function SettingsModal({ onClose }) {
    const [openrouterKey, setOpenrouterKey] = useState('');
    const [status, setStatus] = useState('');
    const [saved, setSaved] = useState(false);

    const handleSave = async () => {
        try {
            await axios.post(`${API_URL}/settings/keys`, {
                openai_api_key: openrouterKey, // Backend uses this field name
            });
            setSaved(true);
            setStatus('Keys saved successfully!');
            setTimeout(() => {
                setSaved(false);
                onClose();
            }, 1500);
        } catch (e) {
            setStatus('Failed to save keys.');
        }
    };

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
            background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(5px)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 1000
        }}>
            <div className="glass-panel" style={{ width: '450px', padding: '2rem', position: 'relative' }}>
                <button onClick={onClose} style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                    <X size={20} />
                </button>

                <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: 0 }}>
                    <Key size={20} color="var(--brand-primary)" /> API Configuration
                </h2>

                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                    We now use <strong style={{ color: 'var(--brand-primary)' }}>OpenRouter</strong> for unified access to GPT-4o, Claude, Gemini, and 20+ other models with a single API key.
                </p>

                <div style={{ marginBottom: '1.5rem' }}>
                    <label style={{
                        display: 'block',
                        fontSize: '0.85rem',
                        fontWeight: 600,
                        marginBottom: '0.5rem',
                        color: 'var(--text-primary)'
                    }}>
                        <Key size={14} style={{ marginRight: '0.3rem', verticalAlign: 'middle' }} />
                        OpenRouter API Key
                    </label>
                    <input
                        type="password"
                        value={openrouterKey}
                        onChange={(e) => setOpenrouterKey(e.target.value)}
                        placeholder="sk-or-v1-..."
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
                        Get your key at <a href="https://openrouter.ai/keys" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--brand-primary)', textDecoration: 'none' }}>openrouter.ai/keys</a>
                    </div>
                </div>

                {status && <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: status.includes('Success') ? 'var(--brand-secondary)' : 'var(--brand-danger)' }}>{status}</div>}

                <button
                    onClick={handleSave}
                    className="btn-primary"
                    style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem' }}
                >
                    {saved ? (
                        <>
                            <Check size={18} /> Saved!
                        </>
                    ) : (
                        <>
                            <Save size={18} /> Save API Key
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}
