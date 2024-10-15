// RankingWidget.js
import React, { useState, useEffect } from 'react';

function RankingWidget({ onSend, item_dict = {}, isSending }) {
  const [rankings, setRankings] = useState({});
  const [error, setError] = useState('');

  const itemKeys = Object.keys(item_dict);
  const numItems = itemKeys.length;

  useEffect(() => {
    // Initialize rankings only if the length of rankings and itemKeys differs
    if (itemKeys.length !== Object.keys(rankings).length) {
      const initialRankings = {};
      itemKeys.forEach((key) => {
        initialRankings[key] = ''; // Ensure initialization to empty string
      });
      setRankings(initialRankings); // Set initial rankings
    }
  }, [item_dict, itemKeys.length, rankings]);

  const handleChange = (key, value) => {
    // Update the ranking for the given item key
    setRankings((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const validateRankings = () => {
    const values = Object.values(rankings).map((val) => parseInt(val, 10));
    // Check if all values are numbers between 1 and numItems
    for (let val of values) {
      if (isNaN(val) || val < 1 || val > numItems) {
        setError(`Please enter numbers between 1 and ${numItems}`);
        return false;
      }
    }
    // Check for duplicates
    const uniqueValues = new Set(values);
    if (uniqueValues.size !== numItems) {
      setError('Each ranking must be unique');
      return false;
    }
    setError('');
    return true;
  };

  const handleSend = () => {
    if (validateRankings()) {
      onSend(rankings);
    }
  };

  return (
    <div className="ranking-widget">
      <form className="ranking-form">
        {itemKeys.map((key) => (
          <div key={key} className="ranking-item">
            <label className="ranking-label">
              <select
                className="ranking-dropdown"
                value={rankings[key] || ''}
                onChange={(e) => handleChange(key, e.target.value)}
                disabled={isSending}
              >
                <option value="">Rank</option>
                {Array.from({ length: numItems }, (_, i) => i + 1).map((num) => (
                  <option key={num} value={num}>
                    {num}
                  </option>
                ))}
              </select>
              <span className="ranking-text">{item_dict[key]}</span>
            </label>
          </div>
        ))}
      </form>
      {error && <div className="error">{error}</div>}
      <button className="send-button" onClick={handleSend} disabled={isSending}>
        Send
      </button>
    </div>
  );
  
}

export default RankingWidget;
