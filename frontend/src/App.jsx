import React, { useState, useEffect } from 'react';
import { AuthProvider } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import ChatConsole from './components/Chat/ChatConsole';
import KBManager from './components/KB/KBManager';
import AuditLogs from './components/Audit/AuditLogs';

function MainApp() {
  const [activeTab, setActiveTab] = useState('chat');
  const [selectedKB, setSelectedKB] = useState('ALL');
  const [knowledgeBases, setKnowledgeBases] = useState([]);

  const fetchKnowledgeBases = async () => {
    try {
      const res = await fetch('/api/v1/kb');
      if (res.ok) {
        const data = await res.json();
        setKnowledgeBases(data);
      }
    } catch (err) {
      console.error("Error fetching knowledge bases:", err);
    }
  };

  useEffect(() => {
    fetchKnowledgeBases();
  }, []);

  return (
    <div className="app-container">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="main-content">
        <Navbar
          selectedKB={selectedKB}
          setSelectedKB={setSelectedKB}
          knowledgeBases={knowledgeBases}
        />
        {activeTab === 'chat' && <ChatConsole selectedKB={selectedKB} />}
        {activeTab === 'kb' && <KBManager knowledgeBases={knowledgeBases} refreshData={fetchKnowledgeBases} />}
        {(activeTab === 'audit' || activeTab === 'health') && <AuditLogs activeTab={activeTab} />}
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}
