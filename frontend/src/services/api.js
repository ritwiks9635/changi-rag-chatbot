// src/services/api.js
import axios from "axios";

// Base API instance
// Uses environment variable for flexibility between dev/prod
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000, // 10 seconds timeout for better UX
});

// Function to send query to backend
export const askQuestion = async (query) => {
  try {
    const response = await apiClient.post("/ask", { query });
    return response.data; // { answer: "..." }
  } catch (error) {
    console.error("API Error:", error);

    // Handle API error gracefully
    if (error.response) {
      // Server responded with error code
      throw new Error(
        error.response.data?.detail || "Server returned an error"
      );
    } else if (error.request) {
      // Request was made but no response
      throw new Error("No response from server. Please check connection.");
    } else {
      // Something else happened
      throw new Error("Request error: " + error.message);
    }
  }
};

export default apiClient;
