// src/components/ChatBox.jsx
import React, { useEffect, useRef, useState } from "react";
import { askQuestion } from "../services/api";

const formatTime = (date = new Date()) =>
  date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

const ChatBox = () => {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hi! How can I help with your trading questions today?", at: formatTime() },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const endRef = useRef(null);

  // always scroll to newest message
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async () => {
    const q = input.trim();
    if (!q || loading) return;

    setErr("");
    setLoading(true);

    // push user message
    setMessages(prev => [...prev, { sender: "user", text: q, at: formatTime() }]);
    setInput("");

    // show typing indicator
    setMessages(prev => [...prev, { sender: "bot-typing", at: formatTime() }]);

    try {
      const { answer } = await askQuestion(q);

      // replace typing with real bot message
      setMessages(prev => {
        const withoutTyping = prev.filter(m => m.sender !== "bot-typing");
        return [...withoutTyping, { sender: "bot", text: answer || "…" , at: formatTime() }];
      });
    } catch (e) {
      setMessages(prev => prev.filter(m => m.sender !== "bot-typing"));
      setErr(e.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <>
      {/* Messages */}
      {messages.map((m, i) => {
        if (m.sender === "bot-typing") {
          return (
            <div key={`t-${i}`} className="msg-row is-bot">
              <img
                src={`${process.env.PUBLIC_URL}/bot_logo.png`}
                className="avatar"
                alt="Assistant"
              />
              <div className="bubble">
                <div className="typing">
                  <span></span><span></span><span></span>
                </div>
                <span className="time">Typing…</span>
              </div>
            </div>
          );
        }

        const isUser = m.sender === "user";
        return (
          <div key={i} className={`msg-row ${isUser ? "is-user" : "is-bot"}`}>
            {!isUser && (
              <img
                src={`${process.env.PUBLIC_URL}/bot_logo.png`}
                className="avatar"
                alt="Assistant"
              />
            )}

            <div className="bubble">
              {m.text}
              <span className="time">{m.at}</span>
            </div>

            {isUser && (
              <img
                src={`${process.env.PUBLIC_URL}/user_img.png`}
                className="avatar"
                alt="You"
              />
            )}
          </div>
        );
      })}

      {/* Error banner (if any) */}
      {err && <div className="error">{err}</div>}

      {/* Composer (input + send) */}
      <div className="composer" style={{ position: "sticky", bottom: 0 }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Reply …"
          aria-label="Type your question"
        />
        <button className="btn-send" onClick={send} disabled={loading || !input.trim()}>
          ➤
        </button>
      </div>

      <div ref={endRef} />
    </>
  );
};

export default ChatBox;
