import React, { useState } from "react";

function SearchForm({ activeTab, onSearch, onSuggestion, onReference }) {
  const [problem, setProblem] = useState("");
  const [reference, setReference] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    if (activeTab === "problem" && problem.trim()) {
      onSuggestion(problem);
    } else if (activeTab === "reference" && reference.trim()) {
      onReference(reference);
    }
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit}>
        {activeTab === "problem" && (
          <div className="form-group">
            <label htmlFor="problem">Describe your problem or situation:</label>
            <textarea
              id="problem"
              className="form-control"
              value={problem}
              onChange={(e) => setProblem(e.target.value)}
              placeholder="Describe your situation or problem..."
              rows="4"
              required
            />
          </div>
        )}

        {activeTab === "reference" && (
          <div className="form-group">
            <label htmlFor="reference">Verse Reference:</label>
            <input
              type="text"
              id="reference"
              className="form-control"
              value={reference}
              onChange={(e) => setReference(e.target.value)}
              placeholder="e.g., 2:255 or 24:35"
              required
            />
          </div>
        )}

        <button type="submit" className="btn btn-primary">
          {activeTab === "problem" && "Get Suggestion"}
          {activeTab === "reference" && "Look Up"}
        </button>
      </form>
    </div>
  );
}

export default SearchForm;
