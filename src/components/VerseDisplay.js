import React, { useState, useEffect } from "react";
import ArabicText from "./ArabicText";
import UrduText from "./UrduText";
import { generateTafseer } from "../api/quranApi";
import Loading from "./Loading";

function VerseDisplay({ verse, showTafseer = false }) {
  const [engTafseer, setEngTafseer] = useState(verse.eng_tafseer || "");
  const [urduTafseer, setUrduTafseer] = useState(verse.urdu_tafseer || "");
  const [loadingTafseer, setLoadingTafseer] = useState(false);
  const [tafseerDisplayed, setTafseerDisplayed] = useState(showTafseer);
  const [error, setError] = useState("");

  useEffect(() => {
    // If tafseer should be shown automatically and it's not already loaded
    if (showTafseer && !engTafseer && !urduTafseer) {
      handleGenerateTafseer();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleGenerateTafseer = async () => {
    if (loadingTafseer) return;

    setLoadingTafseer(true);
    setError("");

    try {
      // Generate English tafseer
      const englishTafseer = await generateTafseer(
        verse.verse_key,
        verse.eng_translation,
        "english"
      );

      // Generate Urdu tafseer
      const urduTafseerText = await generateTafseer(
        verse.verse_key,
        verse.urdu_translation,
        "urdu"
      );

      setEngTafseer(englishTafseer);
      setUrduTafseer(urduTafseerText);
      setTafseerDisplayed(true);
    } catch (err) {
      setError("Error generating tafseer. Please try again.");
      console.error(err);
    } finally {
      setLoadingTafseer(false);
    }
  };

  return (
    <div className="verse-display">
      <ArabicText text={verse.arabic} verseKey={verse.verse_key} />

      <div className="translations-container">
        <div className="section-title">English Translation</div>
        <div className="english-text">
          {(() => {
            // Clean HTML tags from English translation
            const tempDiv = document.createElement("div");
            tempDiv.innerHTML = verse.eng_translation || "";
            return tempDiv.textContent || tempDiv.innerText || "";
          })()}
        </div>

        <UrduText text={verse.urdu_translation} />
      </div>

      {!tafseerDisplayed && !loadingTafseer && (
        <button className="btn btn-secondary" onClick={handleGenerateTafseer}>
          Generate Tafseer
        </button>
      )}

      {loadingTafseer && <Loading />}

      {error && <div className="error-message">{error}</div>}

      {tafseerDisplayed && (
        <div className="tafseer-sections">
          <div className="section-title">English Tafseer</div>
          <div className="english-text tafseer-container">
            {(() => {
              // Clean HTML tags from English tafseer
              const tempDiv = document.createElement("div");
              tempDiv.innerHTML = engTafseer || "";
              return tempDiv.textContent || tempDiv.innerText || "";
            })()}
          </div>

          <UrduText text={urduTafseer} isTafseer={true} />
        </div>
      )}
    </div>
  );
}

export default VerseDisplay;
