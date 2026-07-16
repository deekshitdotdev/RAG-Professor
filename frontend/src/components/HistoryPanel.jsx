import React from 'react';

export default function HistoryPanel({ history, onSelect, onClear }) {
  const items = [...history].reverse();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
      <div className="section-label" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>History</span>
        <button className="clear-history" onClick={onClear}>clear</button>
      </div>
      <div className="history-list">
        {items.map((h, i) => (
          <button key={i} className="history-item" title={h.query} onClick={() => onSelect(h.query)}>
            {h.query}
          </button>
        ))}
      </div>
    </div>
  );
}
