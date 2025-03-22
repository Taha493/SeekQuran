import axios from "axios";

// Base URL for the backend API
const API_BASE_URL = "http://localhost:5000/api";

// API key for Gemini (in a real app, this should be stored securely)
const GEMINI_API_KEY = "AIzaSyBTRbTS4FqpBgrJ05dqfgp4g4yxxcdtxes";

/**
 * Search Quran by keywords
 * @param {string} query - Search query
 * @param {number} numResults - Number of results to return
 * @returns {Promise} - Promise resolving to search results
 */
export const searchByKeywords = async (query, numResults = 3) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/search`, {
      query,
      numResults,
    });
    return response.data;
  } catch (error) {
    console.error("Error searching Quran:", error);
    throw error;
  }
};

/**
 * Get verse by reference
 * @param {string} reference - Verse reference (e.g. "2:255")
 * @returns {Promise} - Promise resolving to verse data
 */
export const getVerseByReference = async (reference) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/verse/${reference}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching verse:", error);
    throw error;
  }
};

/**
 * Get AI-suggested verse for a problem
 * @param {string} problem - Problem description
 * @returns {Promise} - Promise resolving to suggested verse with tafseer
 */
export const getSuggestedVerse = async (problem) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/suggest`, {
      problem,
      apiKey: GEMINI_API_KEY,
    });
    return response.data;
  } catch (error) {
    console.error("Error getting verse suggestion:", error);
    throw error;
  }
};

/**
 * Generate tafseer for a verse
 * @param {string} verseKey - Verse reference
 * @param {string} translation - Verse translation text
 * @param {string} language - Language for tafseer (english or urdu)
 * @returns {Promise} - Promise resolving to tafseer text
 */
export const generateTafseer = async (verseKey, translation, language) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/tafseer`, {
      verseKey,
      translation,
      language,
      apiKey: GEMINI_API_KEY,
    });
    return response.data.tafseer;
  } catch (error) {
    console.error("Error generating tafseer:", error);
    throw error;
  }
};
