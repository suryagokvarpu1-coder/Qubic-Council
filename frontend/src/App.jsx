import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import InputSection from './components/InputSection';
import ConsensusView from './components/ConsensusView';
import NodeInspector from './components/NodeInspector';
import PeerReviewPanel from './components/PeerReviewPanel';
import SettingsModal from './components/SettingsModal';
import HistoryPanel from './components/HistoryPanel';
import { Layout, Settings, History, X } from 'lucide-react';

const API_URL = "http://localhost:8000";

function App() {
  const [graphState, setGraphState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [loadingStage, setLoadingStage] = useState('');

  const handleRun = async (prompt) => {
    setLoading(true);
    setError(null);
    setGraphState(null);

    // Simulate loading stages
    const stages = [
      'Normalizing prompt...',
      'Querying models in parallel...',
      'Extracting claims...',
      'Conducting peer review...',
      'Scoring confidence...',
      'Synthesizing consensus...'
    ];

    let stageIndex = 0;
    const stageInterval = setInterval(() => {
      if (stageIndex < stages.length) {
        setLoadingStage(stages[stageIndex]);
        stageIndex++;
      }
    }, 2000);

    try {
      const response = await axios.post(`${API_URL}/run`, { prompt });
      setGraphState(response.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || err.message || "Failed to connect to Consensus Engine");
    } finally {
      clearInterval(stageInterval);
      setLoading(false);
      setLoadingStage('');
    }
  };

  const loadConversation = async (conversationId) => {
    try {
      const response = await axios.get(`${API_URL}/conversations/${conversationId}`);
      setGraphState(response.data.state);
      setIsHistoryOpen(false);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="container">
      <header style={{
        padding: '1rem 0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '2rem',
        borderBottom: '1px solid var(--glass-border)',
        paddingBottom: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '40px',
            height: '40px',
            background: 'linear-gradient(135deg, var(--brand-primary), var(--brand-secondary))',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(127, 90, 240, 0.3)'
          }}>
            <Layout size={22} color="white" />
          </div>
          <div>
            <span style={{ fontWeight: 700, fontSize: '1.2rem', letterSpacing: '-0.02em', display: 'block' }}>
              Consensus Engine
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>v2.0 with Peer Review</span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={() => setIsHistoryOpen(true)}
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--glass-border)',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              fontSize: '0.9rem'
            }}
          >
            <History size={18} /> History
          </button>
          <button
            onClick={() => setIsSettingsOpen(true)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem'
            }}
          >
            <Settings size={20} />
          </button>
        </div>
      </header>

      <main>
        <InputSection onRun={handleRun} isLoading={loading} />

        {loading && (
          <div className="glass-panel animate-fade-in" style={{
            padding: '2rem',
            textAlign: 'center',
            marginBottom: '2rem'
          }}>
            <div className="loading-spinner" style={{ marginBottom: '1rem' }}></div>
            <div style={{ color: 'var(--brand-primary)', fontWeight: 500 }}>{loadingStage}</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
              This may take 15-30 seconds as we query multiple models...
            </div>
          </div>
        )}

        {error && (
          <div style={{
            padding: '1rem',
            borderRadius: '8px',
            background: 'rgba(239, 69, 101, 0.1)',
            border: '1px solid var(--brand-danger)',
            color: 'var(--brand-danger)',
            textAlign: 'center',
            marginBottom: '2rem'
          }}>
            {error}
          </div>
        )}

        {graphState && (
          <>
            <ConsensusView finalData={graphState.consensus} />

            {graphState.peer_reviews && graphState.peer_reviews.length > 0 && (
              <PeerReviewPanel reviews={graphState.peer_reviews} />
            )}

            <NodeInspector graphState={graphState} />
          </>
        )}
      </main>

      {isSettingsOpen && <SettingsModal onClose={() => setIsSettingsOpen(false)} />}
      {isHistoryOpen && <HistoryPanel onClose={() => setIsHistoryOpen(false)} onSelect={loadConversation} />}
    </div>
  );
}

export default App;
