import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";

const App = () => {
  return (
    <Router>
      <Routes>
        {/* Home Page */}
        <Route path="/" element={<Home />} />

        {/* 404 Page */}
        <Route
          path="*"
          element={
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
              <h1 className="text-5xl font-bold text-gray-800 mb-4">404</h1>
              <p className="text-gray-600">Page not found</p>
              <a
                href="/"
                className="mt-6 px-6 py-3 bg-blue-600 text-white text-lg rounded-lg shadow hover:bg-blue-700 transition"
              >
                Go Home
              </a>
            </div>
          }
        />
      </Routes>
    </Router>
  );
};

export default App;
