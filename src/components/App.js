import React, { useState } from "react";
import "../styles/App.css";
import Header from "./Header";
import SearchForm from "./SearchForm";
import VerseDisplay from "./VerseDisplay";
import Loading from "./Loading";
import {
  searchByKeywords,
  getSuggestedVerse,
  getVerseByReference,
} from "../api/quranApi";

function App() {
  const [activeTab, setActiveTab] = useState("problem");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  const handleSearch = async (query, numResults = 3) => {
    setLoading(true);
    setError("");
    try {
      const response = await searchByKeywords(query, numResults);
      setResults(response);
    } catch (err) {
      setError("Error searching the Quran. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestion = async (problem) => {
    setLoading(true);
    setError("");
    try {
      const response = await getSuggestedVerse(problem);
      setResults([response]); // Wrap in array to use same display component
    } catch (err) {
      setError("Error getting verse suggestion. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleReference = async (reference) => {
    setLoading(true);
    setError("");
    try {
      const response = await getVerseByReference(reference);
      setResults([response]); // Wrap in array to use same display component
    } catch (err) {
      setError("Error fetching the verse. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header />

      <div className="tabs">
        <button
          className={`tab ${activeTab === "problem" ? "active" : ""}`}
          onClick={() => setActiveTab("problem")}
        >
          Get Suggested Verse
        </button>
        <button
          className={`tab ${activeTab === "reference" ? "active" : ""}`}
          onClick={() => setActiveTab("reference")}
        >
          Look up by Reference
        </button>
      </div>

      <SearchForm
        activeTab={activeTab}
        onSearch={handleSearch}
        onSuggestion={handleSuggestion}
        onReference={handleReference}
      />

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <Loading />
      ) : (
        results.length > 0 && (
          <div className="results-container">
            {results.map((verse, index) => (
              <VerseDisplay
                key={`${verse.verse_key}-${index}`}
                verse={verse}
                showTafseer={activeTab === "problem"} // Auto-show tafseer for problem tab
              />
            ))}
          </div>
        )
      )}
    </div>
  );
}

export default App;
