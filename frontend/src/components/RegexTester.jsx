// Client-side regex evaluation fallback
function evaluateClientRegex(title, description) {
  const fullText = (title + " " + description).toLowerCase();
  const isRental = /(cho\s*thu[êe]|thu[êe]|m[ướu]n)/i.test(fullText) && !/(cần\s*bán|bán\s*gấp|giá\s*bán)/i.test(fullText);
  const isBongSao = /b[ôo]ng\s*sao/i.test(fullText);
  
  let blockMatched = null;
  if (/(block|lô|lo)\s*b1|\bb1\b/i.test(fullText)) {
    blockMatched = "Block B1";
  } else if (/(block|lô|lo)\s*b\b/i.test(fullText)) {
    blockMatched = "Block B (Lô B)";
  }

  let bedrooms = null;
  if (/2\s*(pn|phòng\s*ngủ|phong\s*ngu|bed|br)/i.test(fullText) || /2pn/i.test(fullText)) {
    bedrooms = 2;
  }

  let bathrooms = null;
  if (/2\s*(wc|vệ\s*sinh|ve\s*sinh|phòng\s*tắm|bath)/i.test(fullText) || /2wc/i.test(fullText)) {
    bathrooms = 2;
  }

  const phoneMatch = fullText.match(/0[35789]\d{8}/);
  const phone = phoneMatch ? phoneMatch[0] : null;

  const isMatch = isRental && isBongSao && (blockMatched !== null) && (bedrooms === 2) && (bathrooms === 2);

  return {
    is_rental: isRental,
    is_sale_excluded: !isRental,
    block_matched: blockMatched,
    bedrooms: bedrooms,
    bathrooms: bathrooms,
    phone: phone,
    is_match: isMatch
  };
}

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
      if (resp.ok) {
        const data = await resp.json();
        setResult(data);
        return;
      }
    } catch (err) {
      console.warn("Backend not reached, using client-side evaluator:", err);
    } finally {
      setLoading(false);
    }
    // Fallback to client evaluator
    setResult(evaluateClientRegex(title, description));
  };

  return (
    <div className="sandbox-card">
      <div className="section-title" style={{ marginBottom: '0.5rem' }}>
        <Terminal size={20} color="var(--primary)" />
        <span>Regex & Fuzzy Parser Interactive Sandbox</span>
      </div>
      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
        <strong>What this does:</strong> Real estate agents use inconsistent phrasing (e.g. <em>"Lô B1"</em>, <em>"Block B"</em>, <em>"2pn 2wc"</em>, <em>"cần bán"</em>). This sandbox lets you test any sample text to see how the engine parses, extracts contact info, and determines if it qualifies as an exact match.
      </p>

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
