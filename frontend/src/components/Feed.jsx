import React, { useState } from 'react';
import { ExternalLink, Phone, CheckCircle, AlertCircle, Filter, Trash2, Clock, Zap } from 'lucide-react';

export default function Feed({ listings, matchesOnly, setMatchesOnly, onRefresh }) {
  const [clearing, setClearing] = useState(false);

  const handleClearData = async () => {
    if (!window.confirm("Are you sure you want to purge all listings and reset database?")) return;
    setClearing(true);
    try {
      await fetch('/api/clear-data', { method: 'POST' });
      onRefresh();
    } catch (e) {
      console.error("Clear data error:", e);
    } finally {
      setClearing(false);
    }
  };

  const formatFreshness = (item) => {
    if (!item.published_at) {
      return item.is_fresh ? "🕒 Mới phát hiện" : "⏳ Chưa rõ thời gian";
    }
    const pubDate = new Date(item.published_at);
    const now = new Date();
    const diffHours = (now - pubDate) / (1000 * 60 * 60);

    if (diffHours < 1) {
      const mins = Math.max(1, Math.round(diffHours * 60));
      return `⚡ Vừa đăng (${mins} phút trước)`;
    } else if (diffHours < 24) {
      return `🕒 Đăng hôm nay (${Math.round(diffHours)} giờ trước)`;
    } else if (diffHours < 48) {
      return "📅 Đăng hôm qua";
    } else {
      const days = Math.round(diffHours / 24);
      return `⚠️ Đăng ${days} ngày trước (${pubDate.toLocaleDateString('vi-VN')})`;
    }
  };

  return (
    <div>
      <div className="feed-header">
        <div className="section-title">
          <span>Target Listings Feed</span>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 400 }}>
            ({listings.length} Bông Sao listings)
          </span>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <button
            className={`btn-secondary ${matchesOnly ? 'active' : ''}`}
            onClick={() => setMatchesOnly(!matchesOnly)}
            style={{
              borderColor: matchesOnly ? 'var(--primary)' : 'var(--border-color)',
              color: matchesOnly ? 'var(--primary)' : 'var(--text-muted)'
            }}
          >
            <Filter size={16} />
            {matchesOnly ? 'Showing Matches Only' : 'Show All Items'}
          </button>

          <button
            className="btn-secondary"
            onClick={handleClearData}
            disabled={clearing}
            style={{ color: 'var(--danger)', borderColor: 'rgba(239, 68, 68, 0.3)' }}
          >
            <Trash2 size={16} />
            {clearing ? 'Clearing...' : 'Purge All Data'}
          </button>
        </div>
      </div>

      {listings.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
          <AlertCircle size={32} style={{ marginBottom: '0.5rem', opacity: 0.6 }} />
          <p>No listings in database. Click "Trigger Scan Now" or let the 60-second listener run automatically.</p>
        </div>
      ) : (
        <div className="listings-grid">
          {listings.map((item) => (
            <div key={item.id || item.hash_id} className={`listing-card ${item.matches_target ? 'match' : ''}`}>
              <div className="listing-top">
                <div>
                  <span className="source-badge">{item.source}</span>
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noreferrer"
                    className="listing-title"
                    style={{ marginLeft: '0.75rem' }}
                  >
                    {item.title}
                  </a>
                </div>
                <div className="price-tag">{item.price_text}</div>
              </div>

              <div className="tags-row">
                {item.matches_target ? (
                  <span className="pill pill-highlight" style={{ display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                    <Zap size={14} /> FRESH MATCH (< 48H)
                  </span>
                ) : (
                  <span className="pill" style={{ color: 'var(--text-dim)' }}>
                    Bông Sao Listing
                  </span>
                )}

                <span
                  className="pill"
                  style={{
                    color: item.is_fresh ? 'var(--primary)' : 'var(--warning)',
                    borderColor: item.is_fresh ? 'rgba(16, 185, 129, 0.4)' : 'rgba(245, 158, 11, 0.4)'
                  }}
                >
                  <Clock size={12} style={{ marginRight: '0.25rem' }} />
                  {formatFreshness(item)}
                </span>

                {item.block && <span className="pill">{item.block}</span>}
                {item.bedrooms && <span className="pill">{item.bedrooms} Bedrooms</span>}
                {item.bathrooms && <span className="pill">{item.bathrooms} Bathrooms</span>}
                {item.phone && (
                  <span className="pill" style={{ color: 'var(--accent)', borderColor: 'var(--accent)' }}>
                    <Phone size={12} style={{ marginRight: '0.25rem' }} />
                    {item.phone}
                  </span>
                )}
              </div>

              <p className="listing-desc">{item.description}</p>

              <div className="listing-footer">
                <span>
                  {item.published_at
                    ? `Đăng lúc: ${new Date(item.published_at).toLocaleString('vi-VN')} • `
                    : ''}
                  Thu thập lúc: {new Date(item.created_at).toLocaleTimeString('vi-VN')}
                </span>
                <a
                  href={item.url}
                  target="_blank"
                  rel="noreferrer"
                  style={{ color: 'var(--primary)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.25rem', fontWeight: 600 }}
                >
                  Open Listing <ExternalLink size={14} />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
