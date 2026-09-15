import React, { useState, useEffect } from 'react';
import { ShieldCheck, ShieldAlert, Clock, Activity, Database, Cpu, CheckCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function AuditLogs({ activeTab }) {
  const { currentUser } = useAuth();
  const [logs, setLogs] = useState([]);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchAuditData = async () => {
    setLoading(true);
    try {
      if (currentUser.role === 'Admin' || currentUser.role === 'Auditor') {
        const resLogs = await fetch('/api/v1/audit/logs');
        if (resLogs.ok) {
          const dataLogs = await resLogs.json();
          setLogs(dataLogs);
        }
      }

      const resHealth = await fetch('/api/v1/audit/health');
      if (resHealth.ok) {
        const dataHealth = await resHealth.json();
        setHealth(dataHealth);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditData();
  }, [currentUser]);

  if (activeTab === 'health') {
    return (
      <div style={{ flex: 1, padding: '28px 36px', overflowY: 'auto' }}>
        <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.4rem', fontWeight: 700, marginBottom: '6px' }}>System Health & Service Monitor</h2>
        <p style={{ color: 'var(--text-subtle)', fontSize: '0.88rem', marginBottom: '24px' }}>Real-time health status of Relational DB, Vector Database, Embedding Engine, and LLM Provider API.</p>

        {health && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
            <div className="glass-panel" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <Database size={24} className="text-indigo-400" />
                <div>
                  <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Relational Database</h3>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>SQLAlchemy 2.0 + SQLite ORM</span>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#34d399', fontWeight: 600, fontSize: '0.9rem' }}>
                <CheckCircle size={16} />
                <span>{health.database}</span>
              </div>
            </div>

            <div className="glass-panel" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <Activity size={24} className="text-emerald-400" />
                <div>
                  <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Vector Store Adapter</h3>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>ChromaDB / Memory Store</span>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#34d399', fontWeight: 600, fontSize: '0.9rem' }}>
                <CheckCircle size={16} />
                <span>{health.vector_store}</span>
              </div>
            </div>

            <div className="glass-panel" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <Cpu size={24} className="text-violet-400" />
                <div>
                  <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>LLM Provider Engine</h3>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>API / Grounded Synthesis Fallback</span>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#34d399', fontWeight: 600, fontSize: '0.9rem' }}>
                <CheckCircle size={16} />
                <span>{health.llm_provider}</span>
              </div>
            </div>

            <div className="glass-panel" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <ShieldCheck size={24} className="text-cyan-400" />
                <div>
                  <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Embedding Provider</h3>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>Local SentenceTransformers / Hash</span>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#34d399', fontWeight: 600, fontSize: '0.9rem' }}>
                <CheckCircle size={16} />
                <span>{health.embedding_provider}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div style={{ flex: 1, padding: '28px 36px', overflowY: 'auto' }}>
      <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.4rem', fontWeight: 700, marginBottom: '6px' }}>Governance & Query Audit Log</h2>
      <p style={{ color: 'var(--text-subtle)', fontSize: '0.88rem', marginBottom: '24px' }}>Complete audit trail recording user query text, retrieved chunk IDs, execution latency, and prompt injection security defense events.</p>

      {currentUser.role !== 'Admin' && currentUser.role !== 'Auditor' ? (
        <div className="glass-panel" style={{ padding: '30px', textAlign: 'center', color: '#fb7185' }}>
          🔒 Restricted Access: Only users with <b>Admin</b> or <b>Auditor</b> roles have permission to view system audit logs. Switch role in the header to evaluate.
        </div>
      ) : (
        <div className="glass-panel" style={{ padding: '24px' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', color: 'var(--text-subtle)' }}>
                <th style={{ padding: '12px' }}>TIMESTAMP</th>
                <th style={{ padding: '12px' }}>USER / ROLE</th>
                <th style={{ padding: '12px' }}>QUERY TEXT</th>
                <th style={{ padding: '12px' }}>LATENCY</th>
                <th style={{ padding: '12px' }}>PROMPT INJECTION</th>
              </tr>
            </thead>
            <tbody>
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: '30px', color: 'var(--text-subtle)' }}>
                    No audit logs recorded yet. Execute RAG queries in the Assistant tab to generate audit records.
                  </td>
                </tr>
              ) : (
                logs.map((l) => (
                  <tr key={l.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                    <td style={{ padding: '12px', color: 'var(--text-subtle)' }}>{new Date(l.timestamp).toLocaleTimeString()}</td>
                    <td style={{ padding: '12px' }}>
                      <div style={{ fontWeight: 600 }}>{l.user_email}</div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--accent-indigo)' }}>{l.user_role}</div>
                    </td>
                    <td style={{ padding: '12px', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>"{l.query_text}"</td>
                    <td style={{ padding: '12px', fontWeight: 600 }}>{l.response_latency_ms} ms</td>
                    <td style={{ padding: '12px' }}>
                      {l.is_flagged_prompt_injection ? (
                        <span style={{ color: '#fb7185', background: 'rgba(244, 63, 94, 0.15)', padding: '3px 8px', borderRadius: '6px', fontWeight: 600, fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          <ShieldAlert size={12} /> Flagged Attack
                        </span>
                      ) : (
                        <span style={{ color: '#34d399', background: 'rgba(16, 185, 129, 0.15)', padding: '3px 8px', borderRadius: '6px', fontWeight: 600, fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          <ShieldCheck size={12} /> Clean
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
