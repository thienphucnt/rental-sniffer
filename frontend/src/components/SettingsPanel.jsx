import React, { useState } from 'react';
import { Send, CheckCircle, Sliders, Bell } from 'lucide-react';

export default function SettingsPanel() {
  const [testResult, setTestResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleTestNotification = async () => {
    setLoading(true);
    try {
      const resp = await fetch('/api/test-notification', { method: 'POST' });
      const data = await resp.json();
      setTestResult(data);
    } catch (err) {
      console.error("Test notification error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sandbox-card">
      <div className="section-title" style={{ marginBottom: '1.25rem' }}>
        <Sliders size={20} color="var(--primary)" />
        <span>Notification & Anti-Bot Credentials Overview</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
        <div style={{ background: '#090d16', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
          <h4 style={{ color: 'var(--text-main)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Bell size={16} color="var(--primary)" /> Telegram Bot API
          </h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Configured via <code>TELEGRAM_BOT_TOKEN</code> and <code>TELEGRAM_CHAT_ID</code> in <code>.env</code> file.
          </p>
        </div>

        <div style={{ background: '#090d16', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
          <h4 style={{ color: 'var(--text-main)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Bell size={16} color="var(--accent)" /> Discord Webhook
          </h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Configured via <code>DISCORD_WEBHOOK_URL</code> in <code>.env</code> file.
          </p>
        </div>
      </div>

      <button className="btn-primary" onClick={handleTestNotification} disabled={loading}>
        <Send size={16} />
        {loading ? 'Sending Test Alerts...' : 'Trigger Test Telegram & Discord Push Notification'}
      </button>

      {testResult && (
        <div style={{ marginTop: '1.25rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid var(--primary)', padding: '1rem', borderRadius: '8px' }}>
          <p style={{ color: 'var(--primary)', fontWeight: 600, fontSize: '0.9rem' }}>
            {testResult.detail}
          </p>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
            Telegram status: <strong>{testResult.telegram_sent ? 'Sent' : 'Skipped/Failed'}</strong> |
            Discord status: <strong>{testResult.discord_sent ? 'Sent' : 'Skipped/Failed'}</strong>
          </div>
        </div>
      )}
    </div>
  );
}
