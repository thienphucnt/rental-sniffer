import React, { useState } from 'react';
import { Send, CheckCircle, Sliders, Bell } from 'lucide-react';

export default function SettingsPanel() {
  const [testResult, setTestResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleTestNotification = async () => {
    setLoading(true);
    setTestResult(null);
    try {
      const resp = await fetch('/api/test-notification', { method: 'POST' });
      if (!resp.ok) {
        throw new Error(`HTTP error ${resp.status}`);
      }
      const data = await resp.json();
      setTestResult(data);
    } catch (err) {
      console.error("Test notification error:", err);
      setTestResult({
        discord_sent: false,
        detail: "Could not connect to backend server. Make sure `python -m backend.main` is running!"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sandbox-card">
      <div className="section-title" style={{ marginBottom: '1.25rem' }}>
        <Sliders size={20} color="var(--primary)" />
        <span>Discord Alert & Configuration Overview</span>
      </div>

      <div style={{ background: '#090d16', padding: '1.25rem', borderRadius: '10px', border: '1px solid var(--border-color)', marginBottom: '1.5rem' }}>
        <h4 style={{ color: 'var(--accent)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Bell size={18} color="var(--accent)" /> Discord Webhook Integration
        </h4>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
          Configured in your <code>.env</code> file via <code>DISCORD_WEBHOOK_URL</code>.
        </p>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-dim)' }}>
          Status: <strong style={{ color: 'var(--primary)' }}>Active (Auto-pushes on new Bông Sao match)</strong>
        </div>
      </div>

      <button className="btn-primary" onClick={handleTestNotification} disabled={loading}>
        <Send size={16} />
        {loading ? 'Sending Test Alert to Discord...' : 'Trigger Test Discord Notification Now'}
      </button>

      {testResult && (
        <div
          style={{
            marginTop: '1.25rem',
            background: testResult.discord_sent ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
            border: `1px solid ${testResult.discord_sent ? 'var(--primary)' : 'var(--danger)'}`,
            padding: '1rem',
            borderRadius: '8px'
          }}
        >
          <p style={{ color: testResult.discord_sent ? 'var(--primary)' : 'var(--danger)', fontWeight: 600, fontSize: '0.95rem' }}>
            {testResult.detail}
          </p>
        </div>
      )}
    </div>
  );
}
