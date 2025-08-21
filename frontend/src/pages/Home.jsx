// src/pages/Home.jsx
import React from "react";
import ChatBox from "../components/ChatBox";
import "../App.css";

const Home = () => {
  return (
    <div className="page">
      <div className="chat-card">
        {/* Header */}
        <div className="chat-card__header">
          <div className="brand">
            <div className="brand__badge">S</div>
            <div>
              <div className="brand__title">Smart Trading Assistant</div>
              <div className="brand__subtitle">Live AI chat for real-time market Q&amp;A</div>
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="chat-card__body">
          <ChatBox />
        </div>

        {/* Composer */}
        <div className="chat-card__composer">
          {/* The input lives inside ChatBox to keep state & sending together */}
        </div>
      </div>
    </div>
  );
};

export default Home;
