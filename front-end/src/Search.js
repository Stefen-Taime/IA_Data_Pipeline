import React, { useState } from 'react';
import './Search.css';

function SearchBar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    const response = await fetch('http://localhost:5000', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query })
    });
    const data = await response.json();
    setResults(data.response);
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit} className="search-form">
        <input
          className="search-input"
          type="text"
          value={query}
          onChange={event => setQuery(event.target.value)}
        />
        <button className="search-button" type="submit">Search</button>
      </form>
      <div className="results">{results}</div>
    </div>
  );
}

export default SearchBar;
