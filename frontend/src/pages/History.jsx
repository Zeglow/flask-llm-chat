import { useEffect, useState } from 'react';
import axios from '../api/axios';
import { useNavigate } from 'react-router-dom';

function History() {
    const [history, setHistory] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const res = await axios.get('/api/history');
                setHistory(res.data);
            } catch (error) {
                console.error('Error fetching history:', error);
            } finally {
                setIsLoading(false);
            }
        };
        fetchHistory();
    }, []);

    const formatDate = (timestamp) => {
        const date = new Date(timestamp);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const handleChatClick = (chatId) => {
        navigate(`/chat/${chatId}`);
        setIsSidebarOpen(false);
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
                <button 
                    className="btn" 
                    style={{ marginBottom: '1rem' }}
                    onClick={() => {
                        navigate('/chat');
                        setIsSidebarOpen(false);
                    }}
                >
                    New Chat
                </button>
                <div className="history-list">
                    <h3 className="text-sm font-semibold text-gray-500 mb-2 px-2">Recent Conversations</h3>
                    {isLoading ? (
                        <div className="text-center text-gray-500 py-4">Loading...</div>
                    ) : history.length === 0 ? (
                        <div className="text-center text-gray-500 py-4">No conversations yet</div>
                    ) : (
                        history.map((item, index) => (
                            <div
                                key={index}
                                className="history-item"
                                onClick={() => handleChatClick(item.id)}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="truncate">
                                        <div className="font-medium text-gray-900 truncate">
                                            {item.prompt.substring(0, 50)}
                                            {item.prompt.length > 50 ? '...' : ''}
                                        </div>
                                        <div className="text-sm text-gray-500">
                                            {formatDate(item.timestamp)}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            <div className={`overlay ${isSidebarOpen ? 'open' : ''}`} onClick={toggleSidebar} />

            <div className="main-chat">
                <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">Select a conversation</h2>
                        <p className="text-gray-600">Choose a conversation from the sidebar or start a new chat</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default History;