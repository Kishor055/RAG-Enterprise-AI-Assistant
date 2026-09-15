import React, { useState, useEffect } from 'react';
import { UploadCloud, Plus, FileText, Trash2, RefreshCw, Lock, Unlock, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function KBManager({ knowledgeBases, refreshData }) {
  const { currentUser } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedKBForUpload, setSelectedKBForUpload] = useState('');
  const [isPublicUpload, setIsPublicUpload] = useState(true);
  const [allowedRolesStr, setAllowedRolesStr] = useState("Admin,Knowledge Manager,Standard User");
  const [showKBModal, setShowKBModal] = useState(false);
  const [newKBName, setNewKBName] = useState('');
  const [newKBDesc, setNewKBDesc] = useState('');

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/documents');
      if (res.ok) {
        const data = await res.json();
        setDocuments(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
    if (knowledgeBases.length > 0 && !selectedKBForUpload) {
      setSelectedKBForUpload(knowledgeBases[0].id);
    }
  }, [knowledgeBases]);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !selectedKBForUpload) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('knowledge_base_id', selectedKBForUpload);
    formData.append('is_public', isPublicUpload);
    formData.append('allowed_roles', allowedRolesStr);

    try {
      setLoading(true);
      const res = await fetch('/api/v1/documents/upload', {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        fetchDocuments();
        refreshData();
      } else {
        alert("Upload failed. Ensure backend server is running.");
      }
    } catch (err) {
      alert(`Error uploading file: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKB = async () => {
    if (!newKBName.trim()) return;
    try {
      const res = await fetch('/api/v1/kb', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newKBName,
          description: newKBDesc,
          access_level: 'Public'
        })
      });
      if (res.ok) {
        setShowKBModal(false);
        setNewKBName('');
        setNewKBDesc('');
        refreshData();
      }
    } catch (err) {
      alert(`Failed to create KB: ${err.message}`);
    }
  };

  const handleDeleteDoc = async (docId) => {
    if (!confirm("Are you sure you want to delete this document and purge its vector embeddings?")) return;
    try {
      const res = await fetch(`/api/v1/documents/${docId}`, { method: 'DELETE' });
      if (res.ok) {
        fetchDocuments();
        refreshData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleReindexDoc = async (docId) => {
    try {
      setLoading(true);
      const res = await fetch(`/api/v1/documents/${docId}/reindex`, { method: 'POST' });
      if (res.ok) {
        fetchDocuments();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const canManage = currentUser.role === 'Admin' || currentUser.role === 'Knowledge Manager';

  return (
    <div style={{ flex: 1, padding: '28px 36px', overflowY: 'auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.4rem', fontWeight: 700 }}>Knowledge Base & Document Repository</h2>
          <p style={{ color: 'var(--text-subtle)', fontSize: '0.88rem' }}>Upload confidential enterprise files, structure domain knowledge bases, and control Document-Level Security (DLS).</p>
        </div>
        {canManage && (
          <button
            onClick={() => setShowKBModal(true)}
            style={{ background: 'linear-gradient(135deg, var(--accent-indigo), var(--accent-violet))', border: 'none', color: '#fff', padding: '10px 18px', borderRadius: '10px', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}
          >
            <Plus size={16} />
            <span>Create Knowledge Base</span>
          </button>
        )}
      </div>

      {/* Upload Zone */}
      {canManage && (
        <div className="glass-panel" style={{ padding: '24px', marginBottom: '28px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <UploadCloud size={18} className="text-indigo-400" />
            <span>Ingest New Document</span>
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div>
              <label style={{ fontSize: '0.78rem', color: 'var(--text-subtle)', fontWeight: 600, display: 'block', marginBottom: '6px' }}>TARGET KNOWLEDGE BASE</label>
              <select
                value={selectedKBForUpload}
                onChange={(e) => setSelectedKBForUpload(e.target.value)}
                style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', outline: 'none' }}
              >
                {knowledgeBases.map((kb) => (
                  <option key={kb.id} value={kb.id} style={{ background: '#0f172a' }}>{kb.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ fontSize: '0.78rem', color: 'var(--text-subtle)', fontWeight: 600, display: 'block', marginBottom: '6px' }}>DOCUMENT ACCESS LEVEL</label>
              <select
                value={isPublicUpload ? "public" : "private"}
                onChange={(e) => setIsPublicUpload(e.target.value === "public")}
                style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', outline: 'none' }}
              >
                <option value="public" style={{ background: '#0f172a' }}>🌐 Public (All Authorized Employees)</option>
                <option value="private" style={{ background: '#0f172a' }}>🔒 Restricted Role Access</option>
              </select>
            </div>

            {!isPublicUpload && (
              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-subtle)', fontWeight: 600, display: 'block', marginBottom: '6px' }}>ALLOWED ROLES (COMMA-SEPARATED)</label>
                <input
                  type="text"
                  value={allowedRolesStr}
                  onChange={(e) => setAllowedRolesStr(e.target.value)}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', outline: 'none' }}
                  placeholder="Admin,Knowledge Manager"
                />
              </div>
            )}
          </div>

          <label
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '24px',
              border: '2px dashed rgba(99, 102, 241, 0.4)',
              borderRadius: '12px',
              background: 'rgba(99, 102, 241, 0.05)',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            <UploadCloud size={32} style={{ color: 'var(--accent-indigo)', marginBottom: '8px' }} />
            <span style={{ fontSize: '0.92rem', fontWeight: 600 }}>Click to browse or drag & drop files here</span>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-subtle)', marginTop: '4px' }}>Supports PDF, DOCX, TXT, MD, CSV (Up to 50MB)</span>
            <input type="file" onChange={handleFileUpload} style={{ display: 'none' }} accept=".pdf,.docx,.txt,.md,.csv" />
          </label>
        </div>
      )}

      {/* Documents Table */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px' }}>Indexed Enterprise Documents</h3>

        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.88rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', color: 'var(--text-subtle)' }}>
              <th style={{ padding: '12px' }}>DOCUMENT TITLE</th>
              <th style={{ padding: '12px' }}>FILE TYPE</th>
              <th style={{ padding: '12px' }}>STATUS</th>
              <th style={{ padding: '12px' }}>CHUNKS</th>
              <th style={{ padding: '12px' }}>ACCESS LEVEL</th>
              <th style={{ padding: '12px', textAlign: 'right' }}>ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            {documents.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '30px', color: 'var(--text-subtle)' }}>
                  No documents indexed yet. Upload a document above to get started.
                </td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                  <td style={{ padding: '12px', fontWeight: 600 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <FileText size={16} className="text-indigo-400" />
                      <span>{doc.title}</span>
                    </div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', display: 'block', marginTop: '2px' }}>{doc.file_name}</span>
                  </td>
                  <td style={{ padding: '12px', textTransform: 'uppercase', fontWeight: 600, color: 'var(--text-muted)' }}>{doc.file_type}</td>
                  <td style={{ padding: '12px' }}>
                    <span className={`status-pill ${doc.status.toLowerCase()}`}>
                      {doc.status === 'Indexed' && <CheckCircle size={12} />}
                      {doc.status === 'Processing' && <Clock size={12} />}
                      {doc.status === 'Failed' && <AlertCircle size={12} />}
                      {doc.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px', fontWeight: 600 }}>{doc.chunk_count} chunks</td>
                  <td style={{ padding: '12px' }}>
                    {doc.is_public ? (
                      <span style={{ color: '#34d399', fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Unlock size={12} /> Public
                      </span>
                    ) : (
                      <span style={{ color: '#fb7185', fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Lock size={12} /> Restricted ({doc.allowed_roles})
                      </span>
                    )}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    {canManage && (
                      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                        <button
                          onClick={() => handleReindexDoc(doc.id)}
                          title="Re-index vector embeddings"
                          style={{ background: 'rgba(99, 102, 241, 0.15)', border: 'none', color: '#a5b4fc', padding: '6px 10px', borderRadius: '6px', cursor: 'pointer' }}
                        >
                          <RefreshCw size={14} />
                        </button>
                        <button
                          onClick={() => handleDeleteDoc(doc.id)}
                          title="Hard delete document and vectors"
                          style={{ background: 'rgba(244, 63, 94, 0.15)', border: 'none', color: '#fb7185', padding: '6px 10px', borderRadius: '6px', cursor: 'pointer' }}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Create KB Modal */}
      {showKBModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 200 }}>
          <div className="glass-panel" style={{ width: '450px', padding: '24px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '16px' }}>Create Knowledge Base</h3>
            <div style={{ marginBottom: '12px' }}>
              <label style={{ fontSize: '0.78rem', color: 'var(--text-subtle)', fontWeight: 600, display: 'block', marginBottom: '4px' }}>KNOWLEDGE BASE NAME</label>
              <input
                type="text"
                value={newKBName}
                onChange={(e) => setNewKBName(e.target.value)}
                placeholder="e.g. Legal Contracts & NDAs"
                style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff' }}
              />
            </div>
            <div style={{ marginBottom: '20px' }}>
              <label style={{ fontSize: '0.78rem', color: 'var(--text-subtle)', fontWeight: 600, display: 'block', marginBottom: '4px' }}>DESCRIPTION</label>
              <textarea
                value={newKBDesc}
                onChange={(e) => setNewKBDesc(e.target.value)}
                placeholder="Domain description..."
                style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(30, 41, 59, 0.8)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', height: '80px' }}
              />
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button onClick={() => setShowKBModal(false)} style={{ background: 'transparent', border: '1px solid rgba(255,255,255,0.2)', color: '#fff', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer' }}>Cancel</button>
              <button onClick={handleCreateKB} style={{ background: 'linear-gradient(135deg, var(--accent-indigo), var(--accent-violet))', border: 'none', color: '#fff', padding: '8px 16px', borderRadius: '8px', fontWeight: 600, cursor: 'pointer' }}>Save KB</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
