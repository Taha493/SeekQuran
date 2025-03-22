import React from "react";

function ArabicText({ text, verseKey }) {
  return (
    <div className="arabic-text-container">
      <div className="section-title">Arabic Text</div>
      <div className="arabic-text" dir="rtl" lang="ar">
        {text}
      </div>
      {verseKey && <div className="verse-key">{verseKey}</div>}
    </div>
  );
}

export default ArabicText;
