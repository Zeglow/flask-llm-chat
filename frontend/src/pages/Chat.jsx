import { useState, useRef, useEffect } from 'react';
import axios from '../api/axios';

function Chat() {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleChat = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = input.trim();
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setIsLoading(true);

        try {
            const res = await axios.post('/api/chat', { prompt: userMessage });
            setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }]);
        } catch(err) {
            console.error('Chat error:', err);
            setMessages(prev => [...prev, { 
                role: 'assistant', 
                content: 'Sorry, there was an error processing your request.' 
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const toggleSidebar = () => {
        setIsSidebarOpen(!isSidebarOpen);
    };

    return (
        <div className="chat-container">
            <button 
                className="mobile-menu-btn"
                onClick={toggleSidebar}
                aria-label="Toggle menu"
            >
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="3" y1="12" x2="21" y2="12"></line>
                    <line x1="3" y1="6" x2="21" y2="6"></line>
                    <line x1="3" y1="18" x2="21" y2="18"></line>
                </svg>
            </button>

            <div className={`sidebar ${isSidebarOpen ? 'open' : ''}`}>
                <button className="btn" style={{ marginBottom: '1rem' }}>New Chat</button>
                <div className="history-list">
                    {/* 历史记录列表可以在这里添加 */}
                </div>
            </div>

            <div className={`overlay ${isSidebarOpen ? 'open' : ''}`} onClick={toggleSidebar} />

            <div className="main-chat">
                <div className="messages-container">
                    {messages.length === 0 ? (
                        <div style={{ 
                            textAlign: 'center', 
                            marginTop: '2rem',
                            color: 'var(--text-secondary)'
                        }}>
                            <h2>How can I help you today?</h2>
                        </div>
                    ) : (
                        messages.map((message, index) => (
                            <div 
                                key={index} 
                                className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
                            >
                                <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>
                                    {message.role === 'user' ? 'You' : 'Assistant'}
                                </div>
                                <div>{message.content}</div>
                            </div>
                        ))
                    )}
                    {isLoading && (
                        <div className="message assistant-message">
                            <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>Assistant</div>
                            <div>Thinking...</div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
                <div className="input-container">
                    <form onSubmit={handleChat}>
                        <textarea
                            className="message-input"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type your message here..."
                            rows={3}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    handleChat(e);
                                }
                            }}
                        />
                        <button 
                            type="submit" 
                            className="btn"
                            style={{ marginTop: '0.5rem', float: 'right' }}
                            disabled={isLoading}
                        >
                            Send
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default Chat;