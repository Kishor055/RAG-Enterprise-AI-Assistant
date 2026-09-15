import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User as UserIcon, Sparkles, ShieldAlert, FileText, Zap } from 'lucide-react';
import SourceDrawer from './SourceDrawer';
import { useAuth } from '../../context/AuthContext';

export default function ChatConsole({ selectedKB }) {
  const { currentUser } = useAuth();
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'assistant',
      text: "Hello! I am your Enterprise Grounded RAG Assistant. Ask any question about your authorized enterprise policy documents, compliance standards, or standard operating procedures.",
      citations: [],
      latency_ms: 0,
      retrieved_chunks: 0,
      is_injection: false
    }
  ]);

  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeCitations, setActiveCitations] = useState([]);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [activeCitationId, setActiveCitationId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (queryText) => {
    const q = queryText || inputQuery;
    if (!q.trim() || isLoading) return;

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: q
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setIsLoading(true);

    try {
      const kbFilter = selectedKB === 'ALL' ? null : [selectedKB];
      const res = await fetch('/api/v1/rag/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: q,
          knowledge_base_ids: kbFilter,
          top_k: 4
        })
      });

      if (!res.ok) {
        throw new Error("Failed to execute RAG query.");
      }

      const data = await res.json();

      const assistantMsg = {
        id: Date.now() + 1,
        sender: 'assistant',
        text: data.answer,
        citations: data.citations || [],
        latency_ms: data.execution_time_ms,
        retrieved_chunks: data.retrieved_chunk_count,
        is_injection: data.is_flagged_prompt_injection
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'assistant',
          text: `⚠️ Network / Backend Error: ${err.message}. Please verify the FastAPI backend server is active.`,
          citations: []
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const openInspector = (citations, citId = null) => {
    setActiveCitations(citations);
    setActiveCitationId(citId);
    setDrawerOpen(true);
  };

  const renderMessageContent = (msg) => {
    if (msg.sender === 'user') return msg.text;

    return (
      <div>
        {msg.is_injection && (
          <div style={{ background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', padding: '10px 14px', borderRadius: '8px', marginBottom: '12px', color: '#fb7185', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldAlert size={16} />
            <span><b>Security Safety Filter Triggered:</b> Prompt Injection Attempt Flagged</span>
          </div>
        )}

        <div style={{ whiteSpace: 'pre-line', lineHeight: 1.6 }}>{msg.text}</div>

        {msg.citations && msg.citations.length > 0 && (
          <div style={{ marginTop: '14px', paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.08)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-subtle)', fontWeight: 600 }}>RETRIEVED CITATIONS:</span>
              {msg.citations.map((c) => (
                <button
                  key={c.citation_id}
                  className="citation-badge"
                  onClick={() => openInspector(msg.citations, c.citation_id)}
                >
                  <FileText size={12} />
                  <span>#{c.citation_id} {c.document_title} (p.{c.page_number})</span>
                </button>
              ))}
            </div>

            <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Zap size={12} className="text-amber-400" /> {msg.latency_ms} ms</span>
              <span>{msg.retrieved_chunks} chunks</span>
            </div>
          </div>
        )}
      </div>
    );
  };

  const samplePrompts = [
    "What are the remote work laptop security guidelines for 2026?",
    "What is the daily lodging and meal expense reimbursement limit?",
    "How quickly must security breaches or lost laptops be reported?"
  ];

  return (
    <div style={{ display: 'flex', flex: 1, height: '100%', position: 'relative' }}>
      <div className="chat-workspace">
        <div className="messages-list">
          {messages.map((msg) => (
            <div key={msg.id} className={`message-card ${msg.sender}`}>
              <div className={`avatar ${msg.sender}`}>
                {msg.sender === 'user' ? <UserIcon size={18} /> : <Bot size={18} />}
              </div>
              <div className="message-body">
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-subtle)', marginBottom: '4px' }}>
                  {msg.sender === 'user' ? currentUser.full_name : 'Enterprise RAG Assistant'}
                </div>
                {renderMessageContent(msg)}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="message-card assistant">
              <div className="avatar assistant">
                <Bot size={18} />
              </div>
              <div className="message-body" style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-indigo)' }}>
                <Sparkles size={16} className="animate-spin" />
                <span>Searching vector embeddings & synthesizing grounded response...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {messages.length === 1 && (
          <div style={{ margin: '16px 0', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            {samplePrompts.map((p, i) => (
              <button
                key={i}
                onClick={() => handleSend(p)}
                style={{ background: 'rgba(30, 41, 59, 0.6)', border: '1px solid rgba(99, 102, 241, 0.3)', padding: '8px 14px', borderRadius: '20px', color: 'var(--text-muted)', fontSize: '0.82rem', cursor: 'pointer', textAlign: 'left', transition: 'all 0.2s' }}
                onMouseEnter={(e) => e.target.style.background = 'rgba(99, 102, 241, 0.15)'}
                onMouseLeave={(e) => e.target.style.background = 'rgba(30, 41, 59, 0.6)'}
              >
                💡 {p}
              </button>
            ))}
          </div>
        )}

        {/* Input Bar */}
        <div className="input-container">
          <input
            type="text"
            className="chat-input"
            placeholder="Ask a question about enterprise policies, compliance, or uploaded documents..."
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            disabled={isLoading}
          />
          <button className="send-btn" onClick={() => handleSend()} disabled={isLoading}>
            <Send size={16} />
            <span>Ask RAG</span>
          </button>
        </div>
      </div>

      <SourceDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        citations={activeCitations}
        activeCitationId={activeCitationId}
      />
    </div>
  );
}
