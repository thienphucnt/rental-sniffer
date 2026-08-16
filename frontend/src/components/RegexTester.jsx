import React, { useState } from 'react';
import { Terminal, CheckCircle2, XCircle } from 'lucide-react';

export default function RegexTester() {
  const [title, setTitle] = useState("Cho thuê chung cư Bông Sao Block B1 2PN 2WC lầu trung 7.5 triệu");
  const [description, setDescription] = useState("Cho thuê gấp căn hộ Bông Sao lô B1 2 phòng ngủ 2 vệ sinh. Liên hệ 0909123456.");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleTest = async () => {
    setLoading(true);
    try {
      const resp = await fetch('/api/test-regex', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description })
      });
      const data = await resp.json();
      setResult(data);
    } catch (err) {
      console.error("Regex test error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sandbox-card">
      <div className="section-title" style={{ marginBottom: '1rem' }}>
        <Terminal size={20} color="var(--primary)" />
        <span>Regex & Fuzzy Parser Interactive Sandbox</span>
      </div>

      <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>
        Test Listing Title:
      </label>
      <input
        className="input-field"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Enter listing title..."
      />

      <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>
        Test Listing Description:
      </label>
      <textarea
        className="input-field"
        rows={3}
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Enter listing description..."
        style={{ resize: 'vertical' }}
      />

      <button className="btn-primary" onClick={handleTest} disabled={loading}>
        {loading ? 'Evaluating Regex...' : 'Run Regex Test'}
      </button>

      {result && (
        <div style={{ marginTop: '1.5rem', background: '#090d16', padding: '1.25rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            {result.is_match ? (
              <span style={{ color: 'var(--primary)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <CheckCircle2 size={20} /> PASSED MATCH CRITERIA (BLOCK B1, 2PN 2WC, RENT)
              </span>
            ) : (
              <span style={{ color: 'var(--danger)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <XCircle size={20} /> REJECTED / DOES NOT MATCH CRITERIA
              </span>
            )}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem', fontSize: '0.85rem' }}>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Is Rental: </span>
              <strong style={{ color: result.is_rental ? 'var(--primary)' : 'var(--danger)' }}>
                {result.is_rental ? 'Yes (Rent)' : 'No (Excluded)'}
              </strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Block Matched: </span>
              <strong>{result.block_matched || 'None'}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Bedrooms Found: </span>
              <strong>{result.bedrooms ?? 'None'}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Bathrooms Found: </span>
              <strong>{result.bathrooms ?? 'None'}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Phone Extracted: </span>
              <strong style={{ color: 'var(--accent)' }}>{result.phone || 'None'}</strong>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
