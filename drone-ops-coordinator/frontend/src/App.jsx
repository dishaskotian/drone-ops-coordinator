import { useState, useRef, useEffect } from 'react'
import './App.css'

function App() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = inputMessage.trim()
    setInputMessage('')
    setError(null)

    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get response')
      }

      // Add assistant response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response
      }])

    } catch (err) {
      setError(err.message)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${err.message}. Please try again.`
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const resetChat = async () => {
    try {
      await fetch('/api/chat/reset', { method: 'POST' })
      setMessages([])
      setError(null)
    } catch (err) {
      console.error('Failed to reset chat:', err)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const exampleQueries = [
    "Show me all available pilots in Bangalore",
    "Which pilots can work on PRJ001?",
    "Are there any conflicts in the current assignments?",
    "Find me a drone with thermal capabilities",
    "Update pilot P001 status to On Leave"
  ]

  const handleExampleClick = (query) => {
    setInputMessage(query)
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🚁 Drone Operations Coordinator</h1>
          <p className="subtitle">AI-powered fleet management assistant</p>
          <button onClick={resetChat} className="reset-button">
            Reset Conversation
          </button>
        </div>
      </header>

      <main className="main-content">
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <div className="welcome-message">
              <h2>👋 Welcome!</h2>
              <p>I'm your AI assistant for managing drone operations. I can help you with:</p>
              <ul>
                <li>📋 Pilot roster management and availability</li>
                <li>🚁 Drone fleet tracking and status</li>
                <li>🎯 Mission assignments and matching</li>
                <li>⚠️ Conflict detection and resolution</li>
                <li>🔄 Urgent reassignments</li>
              </ul>
              <p className="try-asking">Try asking:</p>
              <div className="example-queries">
                {exampleQueries.map((query, idx) => (
                  <button
                    key={idx}
                    className="example-query"
                    onClick={() => handleExampleClick(query)}
                  >
                    {query}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="messages-container">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  <div className="message-text">{msg.content}</div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message assistant">
                <div className="message-avatar">🤖</div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      <footer className="input-container">
        <div className="input-wrapper">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about pilots, drones, missions, or conflicts..."
            disabled={isLoading}
            rows="1"
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="send-button"
          >
            {isLoading ? '⏳' : '▶️'}
          </button>
        </div>
        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}
      </footer>
    </div>
  )
}

export default App
