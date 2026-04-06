import React, { useState, useRef, useEffect } from 'react';
import './ChatbotInterface.css';

function ChatbotInterface({ messages, onSendMessage, isLoading }) {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (inputValue.trim()) {
      onSendMessage(inputValue);
      setInputValue('');
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <h1 className="chatbot-title">Calendar Booking Agent</h1>
      </div>
      <div className="messages-wrapper">
        <div className="messages-list">
          {messages.map((message) => (
            <div key={message.id} className={`message message-${message.type}`}>
              <div className={`message-bubble message-bubble-${message.type}`}>
                {message.text}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message message-bot">
              <div className="message-bubble message-bubble-bot loading">
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="input-area">
        <div className="input-wrapper">
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
          placeholder="Who would you like to invite?"
          className="chat-input"
          rows="2"
        />
        <button
          onClick={handleSend}
          disabled={!inputValue.trim() || isLoading}
          className="send-button"
            title="Send (Enter)"
          >
            <span className="send-icon">→</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatbotInterface;
