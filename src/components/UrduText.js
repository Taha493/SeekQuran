import React from "react";

function UrduText({ text, isTafseer = false }) {
  // Function to clean any remaining HTML tags
  const cleanText = (text) => {
    if (!text) return "";

    // Create a temporary div element
    const tempDiv = document.createElement("div");
    // Set its HTML content to our text
    tempDiv.innerHTML = text;
    // Return the text content without HTML tags
    return tempDiv.textContent || tempDiv.innerText || "";
  };

  return (
    <div className={isTafseer ? "tafseer-container" : ""}>
      <div className="section-title">
        {isTafseer ? "Urdu Tafseer" : "Urdu Translation"}
      </div>
      <div className="urdu-text" dir="rtl" lang="ur">
        {cleanText(text)}
      </div>
    </div>
  );
}

export default UrduText;
