import React from 'react';
import { useNavigate } from 'react-router-dom';

const Sidebar = ({
    selectedOption, 
    setSelectedOption, 
    setChatHistory, 
    chatHistory, 
    conversations, 
    setConversations, 
    setCurrentConversationId,
    currentConversationId
}) => {
    const navigate = useNavigate();
    
    const handleNewChat = () => {
        // Lưu cuộc trò chuyện hiện tại nếu có
        if (chatHistory.length > 0) {
            const newConversation = {
                id: Date.now(),
                messages: [...chatHistory],
                title: chatHistory[0].image_url ? 'Image Conversation' : (chatHistory[0].content || 'New Conversation')
            };
            setConversations(prev => [...prev, newConversation]);
        }
        // Reset chat history cho cuộc trò chuyện mới
        setChatHistory([]);
        setCurrentConversationId(null);
    };

    const loadConversation = (conversationId) => {
        const conversation = conversations.find(c => c.id === conversationId);
        if (conversation) {
            setChatHistory(conversation.messages);
            setCurrentConversationId(conversationId);
        }
    };

    return (
        <div className="sidebar">
                <button className="back-button" onClick={() => navigate('/')}>
                    <i className="fa fa-home"></i>
                </button>
                <div className="sidebar_title">
                    <h2>Sidebar</h2>
                </div>

                <div className="choices">
                    <select
                        className="options"
                        value={selectedOption}
                        onChange={(e) => setSelectedOption(e.target.value)}
                    >
                        <option value="1">Text to Speech</option>
                        <option value="2">Text to Image</option>
                        <option value="3">Text to Video</option>
                        <option value="4">Create AI Avatar</option>
                        <option value="5">Improve Image Quality</option>
                        <option value="6">AI Chatbox</option>
                        <option value="7">Auto analyze</option>
                    </select>
                </div>

                <div className="new-chat_btn">
                    <button className="generate_btn" onClick={handleNewChat}>
                        + Cuộc trò chuyện mới
                    </button>
                </div>

                <div className="history">
                    <ul className="chat-list" style={{ listStyle: 'none', padding: 0 }}>
                        {conversations.map((conversation) => (
                            <li
                                key={conversation.id}
                                className={`chat-item ${currentConversationId === conversation.id ? 'active' : ''}`}
                                onClick={() => loadConversation(conversation.id)}
                                style={{
                                    padding: '10px',
                                    margin: '5px 0',
                                    cursor: 'pointer',
                                    backgroundColor: currentConversationId === conversation.id ? '#f0f0f0' : 'transparent',
                                    color: currentConversationId === conversation.id ? 'black' : 'white'
                                }}
                            >
                                {conversation.title}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
    );
};

export default Sidebar; 