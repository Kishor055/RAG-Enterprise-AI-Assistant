import React from 'react';
import { MessageSquare, Database, ShieldAlert, Activity, Cpu } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'chat', label: 'RAG Assistant', icon: MessageSquare },
    { id: 'kb', label: 'Knowledge Base', icon: Database },
    { id: 'audit', label: 'Audit & Compliance', icon: ShieldAlert },
    { id: 'health', label: 'System Health', icon: Activity },
  ];

  return (
    <aside className="sidebar">
      <div className="brand-logo">
        <div className="brand-logo-icon">
          <Cpu size={22} className="text-white" />
        </div>
        <div>
          <div className="brand-title">RAG Assistant</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-subtle)', fontWeight: 600 }}>ENTERPRISE AI</div>
        </div>
      </div>

      <nav className="nav-section">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <div
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </div>
          );
        })}
      </nav>

      <div style={{ marginTop: 'auto', paddingTop: '20px', borderTop: '1px solid var(--bg-card-border)' }}>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', marginBottom: '8px', fontWeight: 600 }}>
          PLATFORM SPECS
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          <div>Engine: FastAPI 0.141</div>
          <div>Vector Store: ChromaDB</div>
          <div>LLM: Gemini 1.5 Flash</div>
        </div>
      </div>
    </aside>
  );
}
