// src/services/api.js
import axios from "axios";

// Detect base URL
// For Docker Compose: use "http://backend:8000/api"
// For local dev: "http://localhost:8000/api"
const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://backend:8000/api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

// Function to send query to backend
export const askQuestion = async (query) => {
  try {
    const response = await apiClient.post("/ask", { query });
    return response.data;
  } catch (error) {
    console.error("API Error:", error);

    if (error.response) {
      throw new Error(error.response.data?.detail || "Server returned an error");
    } else if (error.request) {
      throw new Error("No response from server. Please check connection.");
    } else {
      throw new Error("Request error: " + error.message);
    }
  }
};

export default apiClient;
