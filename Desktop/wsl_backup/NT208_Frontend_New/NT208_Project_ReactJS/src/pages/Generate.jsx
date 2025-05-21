import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    EmailShareButton,
    EmailIcon,
    FacebookShareButton,
    FacebookIcon
} from "react-share";
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';

const Generate = () => {
    const navigate = useNavigate();
    const [selectedOption, setSelectedOption] = useState("1");
    const [chatHistory, setChatHistory] = useState([]);
    const [currentConversationId, setCurrentConversationId] = useState(null);
    const [conversations, setConversations] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem("access_token");
        /*         if (!token) {
                    navigate("/login");
                    return;
                } */
    }, [navigate]);

    const handleSubmit = async (text) => {
        if (!text.trim()) {
            alert("Vui lòng nhập nội dung trước khi gửi.");
            return;
        }

        setIsLoading(true);

        // Add user message to chat
        const userMessage = {
            type: 'user',
            content: text
        };
        setChatHistory(prev => [...prev, userMessage]);

        try {
            let apiUrl;
            let requestBody = {};
            let content = null;
            let videoUrl = null;
            if (selectedOption === "1") {
                apiUrl = "http://localhost:8000/text-to-speech";
                requestBody = {
                    text: text,
                    voice: "banmai",
                    speed: "0"
                };
            } else if (selectedOption === "2") {
                apiUrl = "http://localhost:8000/text-to-image/";
                requestBody = {
                    prompt: text,
                    steps: 0
                };
            } else if (selectedOption === "3") {
                apiUrl = "http://localhost:8000/text-to-video";
                requestBody = {
                    prompt: text,
                    negative_prompt: "blurry, low quality, distorted",
                    guidance_scale: 5.0,
                    fps: 16,
                    steps: 30,
                    seed: 123456,
                    frames: 64
                }
            }
            else {
                alert("Tính năng này chưa được hỗ trợ!");
                setIsLoading(false);
                return;
            }

            const response = await fetch(apiUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("access_token")}`
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Lỗi API (${response.status}): ${errorText}`);
            }

            if (selectedOption === "3") {
                const blob = await response.blob();
                videoUrl = URL.createObjectURL(blob);
                content = { video_url: videoUrl };
            } else {
                const data = await response.json();
                content = data;
            }

            // Add bot message to chat
            const botMessage = {
                type: 'bot',
                content,
                option: selectedOption
            };
            setChatHistory(prev => [...prev, botMessage]);

        } catch (error) {
            console.error("Lỗi:", error);
            alert("Có lỗi xảy ra khi gọi API: " + error.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="full-container">
            <Sidebar
                selectedOption={selectedOption}
                setSelectedOption={setSelectedOption}
                chatHistory={chatHistory}
                setChatHistory={setChatHistory}
                conversations={conversations}
                setConversations={setConversations}
                currentConversationId={currentConversationId}
                setCurrentConversationId={setCurrentConversationId}
            />

            <div className="content">
                <Header />

                <div className="conservation content-item">
                    {chatHistory.map((message, index) => (
                        <div key={index} className={`message ${message.type}-message`}>
                            {message.type === 'user' ? (
                                message.content
                            ) : (
                                message.option === "1" ? (
                                    <>
                                        <audio controls src={message.content.audio_url} />
                                        <EmailShareButton subject='My content was created by Nhom1, check it out!'
                                            body='My content was created by Nhom 1! Check it out!' className='share' style={{ color: 'white', margin: '5px' }}>
                                            <EmailIcon size={32} round={true} />
                                        </EmailShareButton>

                                        <FacebookShareButton hashtag='#AI' style={{ color: 'white', margin: '5px' }}>
                                            <FacebookIcon size={32} round={true} />
                                        </FacebookShareButton>
                                    </>
                                ) : message.option === "2" ? (
                                    <><img
                                        src={`http://localhost:8000/${message.content.image_url}`}
                                        alt="Generated"
                                        style={{ maxWidth: '70%', maxHeight: '70%', borderRadius: '10px' }} />
                                        <EmailShareButton subject='My content was created by Nhom1, check it out!'
                                            body='My content was created by Nhom 1! Check it out!' className='share' style={{ color: 'white' }}>
                                            <EmailIcon size={32} round={true} />
                                        </EmailShareButton>

                                        <FacebookShareButton hashtag='#AI'>
                                            <FacebookIcon size={32} round={true} />
                                        </FacebookShareButton>
                                    </>
                                ) : message.option === "3" ? (
                                    <>
                                        <video controls width="100%" src={message.content.video_url} />
                                        <EmailShareButton subject='My content was created by Nhom1, check it out!'
                                            body='My content was created by Nhom 1! Check it out!' className='share' style={{ color: 'white' }}>
                                            <EmailIcon size={32} round={true} />
                                        </EmailShareButton>

                                        <FacebookShareButton hashtag='#AI'>
                                            <FacebookIcon size={32} round={true} />
                                        </FacebookShareButton>
                                    </>
                                ) : null
                            )}
                        </div>
                    ))}
                </div>

                <div className="footer_content content-item">
                    <div id="btn_complex">
                        <textarea
                            className="input"
                            rows="4"
                            placeholder="Mô tả những gì bạn muốn tạo"
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSubmit(e.target.value);
                                    e.target.value = '';
                                }
                            }}
                        />
                        <button
                            id="submit_btn"
                            onClick={(e) => {
                                const textarea = e.target.previousSibling;
                                handleSubmit(textarea.value);
                                textarea.value = '';
                            }}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Đang xử lý...' : 'Create'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Generate; 