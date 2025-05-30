import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

import {
    EmailShareButton,
    EmailIcon,
    FacebookShareButton,
    FacebookIcon
  } from "react-share";

import FileUpload from '../components/FileUpload';

const Generate = () => {
    const navigate = useNavigate();
    const [chatHistory, setChatHistory] = useState([]);
    const [selectedOption, setSelectedOption] = useState("0");
    const [conversations, setConversations] = useState([]);
    const [currentConversationId, setCurrentConversationId] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isManualSelection, setIsManualSelection] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const fileInputRef = useRef(null);

    useEffect(() => {
        const token = localStorage.getItem("access_token");
/*         if (!token) {
            navigate("/login");
            return;
        } */
    }, [navigate]);

    const handleNewChat = () => {
        if (chatHistory.length > 0) {
            const newConversation = {
                id: Date.now(),
                messages: [...chatHistory],
                title: chatHistory[0].content.substring(0, 30) + '...'
            };
            setConversations(prev => [...prev, newConversation]);
        }
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

    const handleAutoAnalyze = async (text) => {
        try {
            const response = await fetch("http://127.0.0.1:8000/analyze", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ user_text: text })
            });

            if (!response.ok) {
                throw new Error(`Lỗi API (${response.status}): ${await response.text()}`);
            }

            const data = await response.json();
            console.log("Auto Analyze Response:", data);

            // Map action sang selectedOption
            const actionMap = {
                "generate_text": "6",
                "generate_image": "2",
                "generate_video": "3",
                "generate_code": "8",
                "generate_speech": "1",
                "generate_answer": "7"
            };
            // đánh dấu

            if (data.intent_analysis && actionMap[data.intent_analysis]) {
                setSelectedOption(actionMap[data.intent_analysis]);
                return {
                    success: true,
                    intent_analysis: data.intent_analysis,
                    prompt: text
                };
            }
            return {
                success: false,
                error: "Không thể xác định chức năng phù hợp"
            };
        } catch (error) {
            console.error("Lỗi khi phân tích:", error);
            return {
                success: false,
                error: error.message
            };
        }
    };

    const handleFileSelect = (event) => {
        const file = event.target.files[0];
        if (file) {
            setSelectedFile(file);
            handleFileUpload(file);
        }
    };

    const handleFileUpload = async (file) => {
        setIsLoading(true);
        const fileExtension = file.name.split('.').pop().toLowerCase();
        const formData = new FormData();
        formData.append("file", file);

        try {
            let apiUrl;
            let fileType;
            // Xác định API dựa trên loại file
            if (["mp4", "avi", "mov"].includes(fileExtension)) {
                apiUrl = "http://127.0.0.1:8000/input/video";
                fileType = "video";
            } else if (["mp3", "wav"].includes(fileExtension)) {
                apiUrl = "http://127.0.0.1:8000/input/speech";
                fileType = "audio";
            } else if (["txt", "doc", "docx", "pdf"].includes(fileExtension)) {
                apiUrl = "http://127.0.0.1:8000/input/document";
                fileType = "document";
            } else {
                alert("Loại file không được hỗ trợ.");
                setIsLoading(false);
                return;
            }

            const response = await fetch(apiUrl, {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Lỗi API (${response.status}): ${await response.text()}`);
            }

            const data = await response.json();
            const extractedText = data.text;

            // Tạo userMessage tùy theo loại file
            let userMessage = {
                type: 'user',
                content: `Đã gửi ${fileType === "video" ? "video" : fileType === "audio" ? "file audio" : "file"}: ${file.name}`
            };

            // Thêm URL tương ứng vào userMessage
            if (fileType === "video") {
                userMessage.video_url = URL.createObjectURL(file);
            } else if (fileType === "audio") {
                userMessage.audio_url = URL.createObjectURL(file);
            } else {
                userMessage.file_url = URL.createObjectURL(file);
            }

            // Thêm userMessage vào chat history
            setChatHistory(prev => [...prev, userMessage]);

            // Gửi text đã trích xuất đến API analyze
            const analyzeResult = await handleAutoAnalyze(extractedText);
            if (analyzeResult.success) {
                // Xử lý tiếp với text đã trích xuất
                await handleSubmit(extractedText);
                // Xóa message user chứa text trích xuất khỏi chatHistory (chỉ khi ở Auto Analyze)
                setChatHistory(prev => prev.filter(m => !(m.type === 'user' && m.content === extractedText)));
            } else {
                alert(analyzeResult.error || "Không thể phân tích nội dung file.");
            }
        } catch (error) {
            console.error("Lỗi khi xử lý file:", error);
            alert("Có lỗi xảy ra khi xử lý file: " + error.message);
        } finally {
            setIsLoading(false);
            setSelectedFile(null);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    const handleOptionChange = (e) => {
        const newValue = e.target.value;
        if (newValue === "0") {
            setIsManualSelection(false);
        } else {
            setIsManualSelection(true);
        }
        setSelectedOption(newValue);
    };

    const handleSubmit = async (text) => {
        if (!text.trim()) {
            alert("Vui lòng nhập nội dung trước khi gửi.");
            return;
        }

        setIsLoading(true);
        const userMessage = {
            type: 'user',
            content: text
        };
        setChatHistory(prev => [...prev, userMessage]);

        try {
            let finalText = text;
            let currentOption = selectedOption;

            // Nếu đang ở chế độ Auto Analyze
            if (selectedOption === "0") {
                const analyzeResult = await handleAutoAnalyze(text);
                if (analyzeResult.success) {
                    // Lấy option mới từ actionMap dựa trên intent_analysis
                    const actionMap = {
                        "generate_text": "6",
                        "generate_image": "2",
                        "generate_video": "3",
                        "generate_code": "8",
                        "generate_speech": "1",
                        "generate_answer": "7"
                    };
                    currentOption = actionMap[analyzeResult.intent_analysis];
                    finalText = analyzeResult.prompt;
                    
                    // Thêm thông báo về chức năng đã được chọn
                    setChatHistory(prev => [
                        ...prev,
                        {
                            type: 'bot',
                            content: { text: `[AutoAnalyze đã xác định chức năng phù hợp]` },
                            option: "0"
                        }
                    ]);
                } else {
                    alert(analyzeResult.error || "Không thể phân tích yêu cầu của bạn. Vui lòng chọn chức năng thủ công.");
                    setIsLoading(false);
                    return;
                }
            }

            console.log("Current Option:", currentOption);
            
            let apiUrl;
            let requestBody = {};
            let videoUrl = null;
            let headers = {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`
            };

            if (currentOption === "1") {
                apiUrl = "http://localhost:8000/text-to-speech";
                requestBody = {
                    text: finalText,
                    voice: "banmai",
                    speed: "0"
                };
            } else if (currentOption === "2") {
                apiUrl = "http://localhost:8000/text-to-image/";
                requestBody = {
                    prompt: finalText,
                    steps: 0
                };
            } else if (currentOption === "3") {
                apiUrl = "http://localhost:8000/text-to-video";
                requestBody = {
                    prompt: finalText,
                    negative_prompt: "blurry, low quality, distorted",
                    guidance_scale: 5.0,
                    fps: 16,
                    steps: 30,
                    seed: 123456,
                    frames: 64
                }
            } else if (currentOption === "6") {
                apiUrl = "http://127.0.0.1:8000/chatbot/content";
                requestBody = {
                    prompt: finalText
                };
                headers = {
                    "Content-Type": "application/json"
                };
            }  else if (currentOption === "7") {
                apiUrl = "http://127.0.0.1:8000/generate_answer";
                requestBody = {
                    question: finalText
                };
                headers = {
                    "Content-Type": "application/json"
                };
            } else if (currentOption === "8") {
                apiUrl = " http://127.0.0.1:8000/text-to-code";
                requestBody = {
                    prompt: finalText
                };
                headers = {
                    "Content-Type": "application/json"
                };
            } else {
                alert("Tính năng này chưa được hỗ trợ!");
                setIsLoading(false);
                return;
            }
            // đánh dấu

            const response = await fetch(apiUrl, {
                method: "POST",
                headers: headers,
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                throw new Error(`Lỗi API (${response.status}): ${await response.text()}`);
            }

            let botMessage;
            if (currentOption === "3") {
                const blob = await response.blob();
                videoUrl = URL.createObjectURL(blob);
                botMessage = {
                    type: 'bot',
                    content: { video_url: videoUrl },
                    option: currentOption
                };
            } else {
                const data = await response.json();
                if (currentOption === "6") {
                    botMessage = {
                        type: 'bot',
                        content: { text: data.response },
                        option: currentOption
                    };
                } else if (currentOption === "2") {
                    botMessage = {
                        type: 'bot',
                        content: { image_url: `http://localhost:8000/${data.image_url}` },
                        option: currentOption
                    };
                } else if (currentOption === "7") {
                    botMessage = {
                        type: 'bot',
                        content: { text: data.answer },
                        option: currentOption
                    };
                } else if (currentOption === "8") {
                    botMessage = {
                        type: 'bot',
                        content: { text: data.code },
                        option: currentOption
                    };
                } else {
                    botMessage = {
                        type: 'bot',
                        content: data,
                        option: currentOption
                    };
                }
            }
            setChatHistory(prev => [...prev, botMessage]);

            // Reset về Auto Analyze nếu không phải là lựa chọn thủ công
            if (!isManualSelection) {
                setSelectedOption("0");
            }

        } catch (error) {
            console.error("Lỗi:", error);
            alert("Có lỗi xảy ra khi gọi API: " + error.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSpeechFile = async (file) => {
        setIsLoading(true);
        const audioUrl = URL.createObjectURL(file);
        const userMessage = {
            type: 'user',
            content: `Đã gửi file audio: ${file.name}`,
            audio_url: audioUrl
        };
        setChatHistory(prev => [...prev, userMessage]);

        try {
            const formData = new FormData();
            formData.append("file", file);

            const response = await fetch("http://127.0.0.1:8000/input/speech", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Lỗi API (${response.status}): ${await response.text()}`);
            }

            const data = await response.json();
            const botMessage = {
                type: 'bot',
                content: { text: data.text },
                option: "8"
            };
            setChatHistory(prev => [...prev, botMessage]);
        } catch (error) {
            alert("Có lỗi xảy ra khi gọi API: " + error.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleVideoFile = async (file) => {
        setIsLoading(true);
        const videoUrl = URL.createObjectURL(file);
        const userMessage = {
            type: 'user',
            content: `Đã gửi video: ${file.name}`,
            video_url: videoUrl
        };
        setChatHistory(prev => [...prev, userMessage]);
    
        try {
            const formData = new FormData();
            formData.append("file", file);
    
            const response = await fetch("http://127.0.0.1:8000/input/video", {
                method: "POST",
                body: formData
            });
    
            if (!response.ok) {
                throw new Error(`Lỗi API (${response.status}): ${await response.text()}`);
            }
    
            const data = await response.json();
    
            const botMessage = {
                type: 'bot',
                content: { text: data.text },
                option: "9"
            };
            setChatHistory(prev => [...prev, botMessage]);
        } catch (error) {
            alert("Gửi video thất bại: " + error.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDocFile = async (file) => {
        setIsLoading(true);
        const fileUrl = URL.createObjectURL(file);
        const userMessage = {
            type: 'user',
            content: `Đã gửi file: ${file.name}`,
            file_url: fileUrl
        };
        setChatHistory(prev => [...prev, userMessage]);

        try {
            const formData = new FormData();
            formData.append("file", file);

            const response = await fetch("http://127.0.0.1:8000/input/file", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Lỗi API (${response.status}): ${await response.text()}`);
            }

            const data = await response.json();
            const botMessage = {
                type: 'bot',
                content: { text: data.text },
                option: "10"
            };
            setChatHistory(prev => [...prev, botMessage]);
        } catch (error) {
            alert("Có lỗi xảy ra khi gọi API: " + error.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleImproveImage = async (file) => {
        setIsLoading(true);
        const imageUrl = URL.createObjectURL(file);
        const userMessage = {
            type: 'user',
            content: `Đã gửi ảnh: ${file.name}`,
            image_url: imageUrl
        };
        setChatHistory(prev => [...prev, userMessage]);

        try {
            const formData = new FormData();
            formData.append("file", file);

            const response = await fetch("http://127.0.0.1:8000/enhance", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Lỗi API (${response.status}): ${await response.text()}`);
            }

            const blob = await response.blob();
            const improvedImageUrl = URL.createObjectURL(blob);
            const botMessage = {
                type: 'bot',
                content: { improved_image_url: improvedImageUrl },
                option: "5"
            };
            setChatHistory(prev => [...prev, botMessage]);
        } catch (error) {
            alert("Có lỗi xảy ra khi gọi API: " + error.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="full-container">
            <div className="sidebar">
                <button className="back-button" onClick={() => navigate('/')}>
                    <i className="fa fa-home"></i>
                </button>
                <div className="sidebar_title">
                    <h2>Sidebar</h2>
                </div>

                <div className="choices">
                    <select
                        className={`options ${isLoading ? 'disabled' : ''}`}
                        value={selectedOption}
                        onChange={handleOptionChange}
                        disabled={isLoading}
                    >
                        <option value="0">Auto Analyze</option>
                        <option value="1">Text to Speech</option>
                        <option value="2">Text to Image</option>
                        <option value="3">Text to Video</option>
                        <option value="4">Create AI Avatar</option>
                        <option value="5">Improve Image Quality</option>
                        <option value="6">AI Chatbox</option>
                        <option value="7">Answer Question</option>
                        <option value="8">Generate code</option>
                        <option value="9">Speech to Text</option>
                        <option value="10">Video to Text</option>
                        <option value="11">File to Text</option>
                    </select>
                </div>

                <div className="new-chat_btn">
                    <button 
                        className={`generate_btn ${isLoading ? 'disabled' : ''}`} 
                        onClick={handleNewChat}
                        disabled={isLoading}
                    >
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
                                    background: currentConversationId === conversation.id ? 'linear-gradient(135deg, #3999ff, #50e2ff)' : 'transparent',
                                    color: currentConversationId === conversation.id ? 'black' : 'white'
                                }}
                            >
                                {conversation.title}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            <div className="content">
                <div className="header_content content-item">
                    <div className="fixed-button-container">
                        <button 
                            className={`rainbow-button fixed-button-advanced ${isLoading ? 'disabled' : ''}`} 
                            onClick={() => navigate('/advanced')}
                            disabled={isLoading}
                        >
                            Advanced
                        </button>
                    </div>
                    <div className="user-info">
                        <i className="fa-solid fa-circle-user fa-2x avatar"></i>
                        <i className="username">User</i>
                    </div>
                </div>

                <div className="conservation content-item">
                    {chatHistory.map((message, index) => (
                        <div
                            key={index}
                            className={`message ${message.type}-message${message.video_url ? " video-message" : ""}${message.audio_url ? " audio-message" : ""}${message.image_url ? " image-message" : ""}`}
                        >
                            {message.type === 'user' ? (
                                message.audio_url ? (
                                    <audio controls src={message.audio_url} />
                                ) : message.video_url ? (
                                    <video
                                        controls
                                        src={message.video_url}
                                        style={{
                                            width: "100%",
                                            maxWidth: "500px",
                                            maxHeight: "300px",
                                            borderRadius: "10px"
                                        }}
                                    />
                                ) : message.image_url ? (
                                    <img
                                        src={message.image_url}
                                        alt="Ảnh đã gửi"
                                        style={{ maxWidth: "300px", borderRadius: "10px" }}
                                    />
                                ) : message.file_url ? (
                                    <a
                                        href={message.file_url}
                                        download
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="file-link"
                                        style={{ fontSize: '30px' }}
                                    >
                                        📄
                                    </a>
                                ) : (
                                    message.content
                                )
                            ) : (
                                message.option === "1" ? (
                                    <>
                                        <audio controls src={message.content.audio_url} />
                                        <EmailShareButton subject='My content was created by Nhom1, check it out!'
                                                body='My content was created by Nhom 1! Check it out!' className='share' style={{color: 'white'}}>
                                                    <EmailIcon size={48} round={true} />
                                        </EmailShareButton>

                                        <FacebookShareButton hashtag='#AI'>
                                            <FacebookIcon size={48} round={true} />
                                        </FacebookShareButton>
                                    </> 
                                ) : message.option === "2" ? (
                                    <>
                                        <img
                                            src={message.content.image_url}
                                            alt="Generated"
                                            style={{ maxWidth: '100%', borderRadius: '10px' }}
                                        />
                                        <EmailShareButton 
                                            subject='My content was created by Nhom1, check it out!'
                                            body='My content was created by Nhom 1! Check it out!' 
                                            className='share' 
                                            style={{color: 'white'}}
                                        >
                                            <EmailIcon size={48} round={true} />
                                        </EmailShareButton>
                                        
                                        <FacebookShareButton hashtag='#AI'>
                                            <FacebookIcon size={48} round={true} />
                                        </FacebookShareButton>
                                    </>
                                ): message.option === "3" ? (
                                    <>
                                        <video controls width="100%" src={message.content.video_url} />
                                        <EmailShareButton subject='My content was created by Nhom1, check it out!'
                                            body='My content was created by Nhom 1! Check it out!' className='share' style={{ color: 'white',borderRadius: '10px' }}>
                                            <EmailIcon size={48} round={true} />
                                        </EmailShareButton>

                                        <FacebookShareButton hashtag='#AI'>
                                            <FacebookIcon size={48} round={true} />
                                        </FacebookShareButton>
                                    </>
                                ) : message.option === "5" ? (
                                    <>
                                        <img
                                            src={message.content.improved_image_url}
                                            alt="Improved"
                                            style={{
                                                width: "100%",
                                                maxWidth: "500px",
                                                maxHeight: "300px",
                                                borderRadius: "10px",
                                                display: "block"
                                            }}
                                        />
                                        <EmailShareButton 
                                            subject='My content was created by Nhom1, check it out!'
                                            body='My content was created by Nhom 1! Check it out!'
                                            className='share' 
                                            style={{color: 'white'}}
                                        >
                                            <EmailIcon size={48} round={true} />
                                        </EmailShareButton>
                                        <FacebookShareButton hashtag='#AI'>
                                            <FacebookIcon size={48} round={true} />
                                        </FacebookShareButton>
                                    </>
                                ) : (message.option === "6" || message.option === "7" || message.option === "8" || message.option === "9" || message.option === "10" || message.option === "11") ? (
                                    <div className="text-response">
                                        {message.content.text}
                                    </div>
                                ) : null
                            )}
                        </div>
                    ))}
                    {isLoading && <div className="loading-spinner"></div>}
                </div>

                <div className="footer_content content-item">
                    <div id="btn_complex" style={{position: 'relative', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                        {selectedOption === "0" ? (
                            // 
                            <>
                            
                         
                                    <textarea
                                        className={`input ${isLoading ? 'disabled' : ''}`}
                                        rows="4"
                                        placeholder="Mô tả những gì bạn muốn tạo, hoặc chọn file để phân tích (Video: .mp4/ Audio: .wav, .mp3/ File: .pdf, .doc, .docx, .txt)"
                                        onKeyDown={(e) => {
                                            if (e.key === 'Enter' && !e.shiftKey) {
                                                e.preventDefault();
                                                handleSubmit(e.target.value);
                                                e.target.value = '';
                                            }
                                        }}
                                        onFocus={() => {
                                            const uploadBtn = document.querySelector('.file-upload-btn');
                                            if (uploadBtn) uploadBtn.style.display = 'none';
                                        }}
                                        onBlur={() => {
                                            const uploadBtn = document.querySelector('.file-upload-btn');
                                            if (uploadBtn) uploadBtn.style.display = 'flex';
                                        }}
                                        disabled={isLoading}
                                    />
                                     <button
                                        className={`file-upload-btn ${isLoading ? 'disabled' : ''}`}
                                        onClick={() => fileInputRef.current?.click()}
                                        disabled={isLoading}
                                        style={{
                                            padding: '10px',
                                            borderRadius: '50%',
                                            height: '20px',
                                            marginLeft: '2%',
                                            marginRight: '20px',
                                            marginBottom: '3%',
                                            width: '20px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            cursor: 'pointer',
                                            background: 'linear-gradient(45deg, #ff00ff, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff)',
                                            border: 'none',
                                            color: 'black',
                                            fontSize: '25px',
                                            position: 'absolute'
                                        }}
                                    >
                                        +
                                    </button>
                                    <div class="glow-wrapper">
                                    <button
                                        id="submit_btn"
                                        className={isLoading ? 'disabled' : ''}
                                        onClick={(e) => {
                                            const textarea = e.target.parentElement.querySelector('textarea');
                                            handleSubmit(textarea.value);
                                            textarea.value = '';
                                        }}
                                        disabled={isLoading}
                                        
                                    >
                                        Create
                                    </button>
                                    </div>
                                <input
                                        type="file"
                                        ref={fileInputRef}
                                        onChange={handleFileSelect}
                                        style={{ display: 'none' }}
                                        accept=".mp4,.wav,.mp3,.pdf,.doc,.docx,.txt"
                                    />
                            
                            </>
                            
                        ) : selectedOption === "9" ? (
                            <div style={{ 
                                display: 'flex', 
                                flexDirection: 'column', 
                                alignItems: 'center', 
                                gap: '10px', 
                                width: '60%',
                                margin: '20px auto'
                            }}>
                                <FileUpload onFileSend={handleSpeechFile} accept=".wav" disabled={isLoading} />
                                <span style={{ color: "#fff" }}>
                                    Hãy chọn file (.wav,.mp3) để chuyển thành văn bản...
                                </span>
                            </div>
                        ) : selectedOption === "10" ? (
                            <div style={{ 
                                display: 'flex', 
                                flexDirection: 'column', 
                                alignItems: 'center', 
                                gap: '10px', 
                                width: '60%',
                                margin: '20px auto'
                            }}>
                                <FileUpload onFileSend={handleVideoFile} accept=".mp4" disabled={isLoading} />
                                <span style={{ color: "#fff" }}>
                                    Hãy chọn file video (.mp4) để chuyển thành văn bản...
                                </span>
                            </div>
                        ) : selectedOption === "11" ? (
                            <div style={{ 
                                display: 'flex', 
                                flexDirection: 'column', 
                                alignItems: 'center', 
                                gap: '10px', 
                                width: '60%',
                                margin: '20px auto'
                            }}>
                                <FileUpload onFileSend={handleDocFile} accept=".docx,.txt" disabled={isLoading} />
                                <span style={{ color: "#fff" }}>
                                    Hãy chọn file (.pdf, .doc, .docx, .txt) để chuyển thành văn bản...
                                </span>
                            </div>
                        ) : selectedOption === "5" ? (
                            <div style={{ 
                                display: 'flex', 
                                flexDirection: 'column', 
                                alignItems: 'center', 
                                gap: '10px', 
                                width: '60%',
                                margin: '20px auto'
                            }}>
                                <FileUpload onFileSend={handleImproveImage} accept=".jpg" disabled={isLoading} />
                                <span style={{ color: "#fff" }}>
                                    Hãy chọn file ảnh (.jpg) để cải thiện chất lượng...
                                </span>
                            </div>
                        ) : (
                            <>
                                <textarea
                                    className={`input ${isLoading ? 'disabled' : ''}`}
                                    rows="4"
                                    placeholder="Mô tả những gì bạn muốn tạo"
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter' && !e.shiftKey) {
                                            e.preventDefault();
                                            handleSubmit(e.target.value);
                                            e.target.value = '';
                                        }
                                    }}
                                    disabled={isLoading}
                                />
                                 <div class="glow-wrapper">
                                <button
                                    id="submit_btn"
                                    className={isLoading ? 'disabled' : ''}
                                    onClick={(e) => {
                                        const textarea = e.target.previousSibling;
                                        handleSubmit(textarea.value);
                                        textarea.value = '';
                                    }}
                                    disabled={isLoading}
                                >
                                    Create
                                </button>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Generate; 