import React from 'react';
import { Activity, Target, Database, Clock, RefreshCw } from 'lucide-react';

export default function StatusOverview({ statusData, onRefresh, isScanning }) {
  const isOnline = statusData && statusData.status !== 'DISCONNECTED';
  const statusText = !isOnline
    ? 'OFFLINE'
    : isScanning || statusData.status === 'SCANNING'
    ? 'SCANNING NOW'
    : 'ONLINE (Listening)';

  return (
    <div className="stats-grid">
      <div className="card">
        <div className="card-header">
          <span>Engine Status</span>
          <Activity size={18} color={isOnline ? "var(--primary)" : "var(--danger)"} />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span
            className="pulse-indicator"
            style={{
              background: isOnline ? 'var(--primary)' : 'var(--danger)',
              boxShadow: `0 0 10px ${isOnline ? 'var(--primary)' : 'var(--danger)'}`
            }}
          />
          <span className="card-value" style={{ fontSize: '1.25rem', color: isOnline ? 'var(--text-main)' : 'var(--danger)' }}>
            {statusText}
          </span>
        </div>
        {!isOnline && (
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Run <code>python -m backend.main</code> in terminal
          </p>
        )}
      </div>

      <div className="card">
        <div className="card-header">
          <span>Total Matches Found</span>
          <Target size={18} color="var(--primary)" />
        </div>
        <div className="card-value" style={{ color: 'var(--primary)' }}>
          {statusData?.total_matches_found ?? 0}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <span>Scraped Items Processed</span>
          <Database size={18} color="var(--accent)" />
        </div>
        <div className="card-value">
          {statusData?.total_scraped_items ?? 0}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <span>Polling Frequency & Filter</span>
          <Clock size={18} color="var(--warning)" />
        </div>
        <div className="card-value" style={{ fontSize: '1.2rem' }}>
          Every {statusData?.poll_interval_seconds ?? 60}s
        </div>
        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
          Max Age: &lt; {statusData?.max_listing_age_hours ?? 48} hours old
        </div>
      </div>
    </div>
  );
}
