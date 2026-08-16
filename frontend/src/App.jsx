import React, { useState, useEffect } from 'react';
import { Play, RefreshCw, Terminal, Layers, Sliders, ShieldCheck } from 'lucide-react';
import StatusOverview from './components/StatusOverview';
import Feed from './components/Feed';
import RegexTester from './components/RegexTester';
import SettingsPanel from './components/SettingsPanel';

export default function App() {
  const [activeTab, setActiveTab] = useState('feed');
  const [statusData, setStatusData] = useState(null);
  const [listings, setListings] = useState([]);
  const [matchesOnly, setMatchesOnly] = useState(false);
  const [loading, setLoading] = useState(false);
  const [triggering, setTriggering] = useState(false);

  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      setStatusData(data);
    } catch (e) {
      console.error("Fetch status error:", e);
    }
  };

  const fetchListings = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/listings?matches_only=${matchesOnly}`);
      const data = await res.json();
      setListings(data);
    } catch (e) {
      console.error("Fetch listings error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchListings();
    const interval = setInterval(() => {
      fetchStatus();
      fetchListings();
    }, 15000);
    return () => clearInterval(interval);
  }, [matchesOnly]);

  const handleManualScan = async () => {
    setTriggering(true);
    try {
      await fetch('/api/trigger-scan', { method: 'POST' });
      await fetchStatus();
      await fetchListings();
    } catch (e) {
      console.error("Trigger scan error:", e);
    } finally {
      setTriggering(false);
    }
  };

  return (
    <div>
      <header className="app-header">
        <div className="header-container">
          <div className="logo-group">
            <span className="logo-badge">BÔNG SAO Q8</span>
            <div>
              <h1 className="header-title">Rental Listings Sniffer</h1>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Target: Block B1 (Lô B) • 2PN 2WC Rent
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <button className="btn-primary" onClick={handleManualScan} disabled={triggering}>
              <Play size={16} />
              {triggering ? 'Scanning...' : 'Trigger Scan Now'}
            </button>

            <nav className="nav-tabs">
              <button
                className={`nav-btn ${activeTab === 'feed' ? 'active' : ''}`}
                onClick={() => setActiveTab('feed')}
              >
                <Layers size={16} /> Feed
              </button>
              <button
                className={`nav-btn ${activeTab === 'regex' ? 'active' : ''}`}
                onClick={() => setActiveTab('regex')}
              >
                <Terminal size={16} /> Regex Sandbox
              </button>
              <button
                className={`nav-btn ${activeTab === 'settings' ? 'active' : ''}`}
                onClick={() => setActiveTab('settings')}
              >
                <Sliders size={16} /> Settings
              </button>
            </nav>
          </div>
        </div>
      </header>

      <main className="main-content">
        <StatusOverview
          statusData={statusData}
          onRefresh={() => { fetchStatus(); fetchListings(); }}
          isScanning={statusData?.status === 'SCANNING'}
        />

        {activeTab === 'feed' && (
          <Feed
            listings={listings}
            matchesOnly={matchesOnly}
            setMatchesOnly={setMatchesOnly}
            onRefresh={fetchListings}
          />
        )}

        {activeTab === 'regex' && <RegexTester />}

        {activeTab === 'settings' && <SettingsPanel />}
      </main>
    </div>
  );
}
