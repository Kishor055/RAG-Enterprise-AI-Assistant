import React from 'react';
import { X, FileText, CheckCircle2, Award, Hash } from 'lucide-react';

export default function SourceDrawer({ isOpen, onClose, citations, activeCitationId }) {
  if (!isOpen) return null;

  return (
    <div className={`source-drawer ${isOpen ? 'open' : ''}`}>
      <div className="drawer-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <FileText size={20} style={{ color: 'var(--accent-indigo)' }} />
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, fontFamily: 'var(--font-heading)' }}>Source Inspector</h3>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>Traceability & Citation Proof</p>
          </div>
        </div>
        <button
          onClick={onClose}
          style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
        >
          <X size={20} />
        </button>
      </div>

      <div className="drawer-body">
        {citations.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'var(--text-subtle)', padding: '40px 0' }}>
            No citation sources retrieved for this message.
          </div>
        ) : (
          citations.map((c, idx) => {
            const isSelected = activeCitationId === c.citation_id;
            return (
              <div
                key={idx}
                className="citation-card"
                style={{
                  borderColor: isSelected ? 'var(--accent-indigo)' : 'rgba(255, 255, 255, 0.08)',
                  background: isSelected ? 'rgba(99, 102, 241, 0.1)' : 'rgba(30, 41, 59, 0.5)'
                }}
              >
                <div className="citation-card-header">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ background: 'var(--accent-indigo)', color: '#fff', fontSize: '0.75rem', padding: '2px 6px', borderRadius: '4px', fontWeight: 700 }}>
                      #{c.citation_id}
                    </span>
                    <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{c.document_title}</span>
                  </div>
                  <span className="score-badge">
                    {Math.round(c.similarity_score * 100)}% Match
                  </span>
                </div>

                <div style={{ fontSize: '0.78rem', color: 'var(--text-subtle)', marginBottom: '10px', display: 'flex', gap: '12px' }}>
                  <span>File: <b>{c.file_name}</b></span>
                  <span>Page: <b>{c.page_number}</b></span>
                </div>

                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', background: 'rgba(15, 23, 42, 0.6)', padding: '10px', borderRadius: '8px', borderLeft: '3px solid var(--accent-indigo)', fontStyle: 'italic', lineHeight: 1.5 }}>
                  "{c.snippet}"
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
