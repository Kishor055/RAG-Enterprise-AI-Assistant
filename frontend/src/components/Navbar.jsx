import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Shield, UserCheck, Layers } from 'lucide-react';

export default function Navbar({ selectedKB, setSelectedKB, knowledgeBases }) {
  const { currentUser, switchRole } = useAuth();

  return (
    <header className="header-bar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(30, 41, 59, 0.6)', padding: '6px 14px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.08)' }}>
          <Layers size={16} className="text-indigo-400" />
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Knowledge Scope:</span>
          <select
            value={selectedKB}
            onChange={(e) => setSelectedKB(e.target.value)}
            style={{ background: 'transparent', border: 'none', color: '#fff', fontSize: '0.88rem', outline: 'none', fontWeight: 600, cursor: 'pointer' }}
          >
            <option value="ALL" style={{ background: '#0f172a' }}>All Authorized Knowledge Bases</option>
            {knowledgeBases.map((kb) => (
              <option key={kb.id} value={kb.id} style={{ background: '#0f172a' }}>{kb.name}</option>
            ))}
          </select>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        {/* Role Switcher Demo Control */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(15, 23, 42, 0.9)', padding: '4px 12px', borderRadius: '10px', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
          <Shield size={14} style={{ color: 'var(--accent-indigo)' }} />
          <span style={{ fontSize: '0.78rem', color: 'var(--text-subtle)', fontWeight: 600 }}>Active Role:</span>
          <select
            value={currentUser.role === 'Admin' ? 'admin' : currentUser.role === 'Knowledge Manager' ? 'manager' : 'employee'}
            onChange={(e) => switchRole(e.target.value)}
            style={{ background: 'transparent', border: 'none', color: 'var(--accent-indigo)', fontSize: '0.82rem', outline: 'none', fontWeight: 700, cursor: 'pointer' }}
          >
            <option value="admin" style={{ background: '#0f172a' }}>Enterprise Admin</option>
            <option value="manager" style={{ background: '#0f172a' }}>Knowledge Manager</option>
            <option value="employee" style={{ background: '#0f172a' }}>Standard Employee</option>
          </select>
        </div>

        {/* User Badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '34px', height: '34px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--accent-indigo), var(--accent-violet))', display: 'flex', alignItems: 'center', justifyCenter: 'center', fontWeight: 700, fontSize: '0.85rem' }}>
            {currentUser.full_name[0]}
          </div>
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{currentUser.full_name}</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--accent-emerald)' }}>{currentUser.role}</div>
          </div>
        </div>
      </div>
    </header>
  );
}
