import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    EmailShareButton, EmailIcon,
    FacebookShareButton, FacebookIcon
} from "react-share";

const Generate = () => {
    const navigate = useNavigate();
    const [chatHistory, setChatHistory] = useState([]);
    const [conversations, setConversations] = useState([]);
    const [currentConversationId, setCurrentConversationId] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    
    const [selectedFile, setSelectedFile] = useState(null);
    const [imagePreview, setImagePreview] = useState(null); 

    const genericFileInputRef = useRef(null);
    const imageInputRef = useRef(null);

    const [userInfo, setUserInfo] = useState({ email: ' ', role: 'free', expire: ' ' });
    const [retryAfter, setRetryAfter] = useState(0);
    const [isRateLimited, setIsRateLimited] = useState(false);
    const [inputValue, setInputValue] = useState('');

    const [currentAiModel, setCurrentAiModel] = useState("1.0");
    const [availableAiModels, setAvailableAiModels] = useState([{ value: "1.0", label: "Model 1.0" }]);

    useEffect(() => {
        const fetchUserInfo = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/user-info', {
                    method: "GET",
                    credentials: 'include',
                });
                const data = await response.json();
                if (data.email) {
                    localStorage.setItem('email', data.email);
                    const userRole = data.role || 'free';
                    setUserInfo({ email: data.email, role: userRole, expire: data.expire || '' });

                    let models = [{ value: "1.0", label: "Model 1.0" }];
                    if (userRole === 'vip') {
                        models.push({ value: "1.1", label: "Model 1.1" });
                    }
                    setAvailableAiModels(models);
                    if (userRole !== 'vip' && currentAiModel === "1.1") {
                        setCurrentAiModel("1.0");
                    }
                } else {
                    alert("Không tìm thấy thông tin người dùng! Vui lòng đăng nhập lại.");
                    // navigate('/login'); 
                }
            } catch (error) {
                console.error("Lỗi khi lấy thông tin người dùng:", error);
                alert("Lỗi kết nối khi lấy thông tin người dùng.");
            }
        };
        fetchUserInfo();
    }, [navigate]);

    const handleNewChat = () => {
        if (chatHistory.length > 0 && currentConversationId === null) {
            const newConversation = {
                id: Date.now(),
                messages: [...chatHistory],
                title: chatHistory[0]?.content?.substring(0, 30) + '...' || 'Cuộc trò chuyện mới'
            };
            setConversations(prev => [...prev, newConversation]);
        }
        setChatHistory([]);
        setCurrentConversationId(null);
        setInputValue('');
        setSelectedFile(null);
        setImagePreview(null);
        if (genericFileInputRef.current) genericFileInputRef.current.value = null;
        if (imageInputRef.current) imageInputRef.current.value = null;
    };

    const loadConversation = (conversationId) => {
        const conversation = conversations.find(c => c.id === conversationId);
        if (conversation) {
            setChatHistory(conversation.messages);
            setCurrentConversationId(conversationId);
        }
    };

    const handleAiModelChange = (e) => {
        setCurrentAiModel(e.target.value);
    };

    const handleFileSelection = (event, fileType) => {
        const file = event.target.files[0];
        if (file) {
            setSelectedFile(file);
            if (fileType === 'image' && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onloadend = () => {
                    setImagePreview(reader.result);
                };
                reader.readAsDataURL(file);
            } else if (fileType === 'image') {
                alert("Vui lòng chọn file ảnh hợp lệ.");
                setSelectedFile(null);
                setImagePreview(null);
                if (imageInputRef.current) imageInputRef.current.value = null;
            } else {
                setImagePreview(null); 
                setChatHistory(prev => prev.filter(msg => !(msg.type === 'user' && msg.content?.startsWith('Đã chọn file:')))); // Xóa tin nhắn "Đã chọn file" cũ nếu có
                setChatHistory(prev => [...prev, {
                    type: 'user',
                    content: `Đã chọn file: ${file.name} (sẵn sàng để gửi cùng mô tả)`
                }]);
            }
        }
    };
    
    const handleSubmit = async () => {
        const textPrompt = inputValue.trim();
        const fileToSubmit = selectedFile;

        if (!textPrompt && !fileToSubmit) {
            alert("Vui lòng nhập mô tả hoặc chọn một file.");
            return;
        }

        setIsLoading(true);
        setInputValue(''); 

        const userMessages = [];
        if (textPrompt) {
            userMessages.push({ type: 'user', content: textPrompt });
        }
        if (fileToSubmit) {
            // Xóa tin nhắn "Đã chọn file:" trước khi thêm tin nhắn "Đã gửi file:"
            setChatHistory(prev => prev.filter(msg => !(msg.type === 'user' && msg.content?.startsWith('Đã chọn file:'))));
            if (imagePreview && fileToSubmit.type.startsWith('image/')) {
                userMessages.push({ type: 'user', image_url: imagePreview, fileName: fileToSubmit.name });
            } else {
                userMessages.push({ type: 'user', content: `Đã gửi file: ${fileToSubmit.name}`, file_obj: fileToSubmit /* Giữ lại để tham chiếu nếu cần */ });
            }
        }
        if (userMessages.length > 0) {
            setChatHistory(prev => [...prev, ...userMessages]);
        }

        const analyzeApiUrl = userInfo.role === 'vip' ?
            'http://localhost:8000/advanced/analyze' :
            'http://localhost:8000/analyze';

        const analyzeFormData = new FormData();
        analyzeFormData.append('text', textPrompt || '');
        if (fileToSubmit) {
            analyzeFormData.append('file', fileToSubmit);
        }

        try {
            const analyzeResponse = await fetch(analyzeApiUrl, {
                method: 'POST',
                headers: {
                    "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
                    'X-User-Email': userInfo.email,
                    'X-User-Role': userInfo.role,
                },
                body: JSON.stringify({ user_text: textPrompt })
            });

            if (analyzeResponse.status === 429) {
                const retryAfterValue = analyzeResponse.headers.get('Retry-After') || "60";
                setRetryAfter(parseInt(retryAfterValue));
                setIsRateLimited(true);
                alert(`Rate limit. Vui lòng thử lại sau ${retryAfterValue} giây.`);
                let remainingTime = parseInt(retryAfterValue);
                const timer = setInterval(() => {
                    setRetryAfter(prev => prev - 1);
                    remainingTime -= 1;
                    if (remainingTime <= 0) {
                        clearInterval(timer);
                        setIsRateLimited(false);
                        setRetryAfter(0);
                    }
                }, 1000);
                setIsLoading(false);
                setChatHistory(prev => prev.slice(0, prev.length - userMessages.length));
                return;
            }

            if (!analyzeResponse.ok) {
                const errorText = await analyzeResponse.text();
                throw new Error(`Lỗi Analyze API (${analyzeResponse.status}): ${errorText}`);
            }

            const analyzeData = await analyzeResponse.json();

            if (!analyzeData.task || analyzeData.task === "unknown_task") {
                throw new Error(analyzeData.detail || "Không thể xác định tác vụ từ yêu cầu của bạn.");
            }

            const taskKey = analyzeData.task;
            const taskParameters = analyzeData.parameters || {};
            const taskDisplayName = taskKey.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            setChatHistory(prev => [...prev, { type: 'bot', content: { text: `[AI đang thực hiện: ${taskDisplayName}]` }, option: "system" }]);

            let finalApiUrl = '';
            let finalRequestBody = { ...taskParameters }; 
            let finalRequestIsFormData = false;
            let responseType = 'json'; 

            finalRequestBody.model_version = currentAiModel;

            switch (taskKey) {
                case "text-to-code":
                    finalApiUrl = "http://localhost:8000/advanced/text-to-code";
                    finalRequestBody.prompt = taskParameters.prompt || textPrompt;
                    finalRequestBody.language = taskParameters.language || "python";
                    break;
                case "text-to-image":
                    finalApiUrl = "http://localhost:8000/advanced/text-to-image";
                    finalRequestBody.prompt = taskParameters.prompt || textPrompt;
                    finalRequestBody.response_format = "url";
                    break;
                case "text-to-audio":
                    finalApiUrl = "http://localhost:8000/advanced/text-to-audio";
                    finalRequestBody.text = taskParameters.input || textPrompt;
                    finalRequestBody.voice = taskParameters.voice || "alloy";
                    finalRequestBody.response_format = "mp3";
                    responseType = 'audio_stream';
                    break;
                case "text-to-video":
                    finalApiUrl = "http://localhost:8000/advanced/text-to-video";
                    finalRequestBody.prompt_text = taskParameters.prompt_text || textPrompt;
                    // Add other necessary params for text-to-video, e.g., from taskParameters
                    finalRequestBody.model = taskParameters.model || "gen-2"; // example
                    finalRequestBody.ratio = taskParameters.ratio || "16:9";
                    finalRequestBody.duration = taskParameters.duration || 4;
                    break;
                case "generate-answer":
                    finalApiUrl = "http://localhost:8000/advanced/generate-answer";
                    finalRequestBody.question = taskParameters.question || textPrompt;
                    finalRequestBody.context = taskParameters.context || "";
                    break;
                case "chatbot-content":
                    finalApiUrl = "http://localhost:8000/advanced/chatbot-content";
                    const chatMessages = chatHistory
                        .filter(msg => msg.type === 'user' || (msg.type === 'bot' && msg.task === "chatbot-content")) 
                        .slice(-10) 
                        .map(msg => ({
                            role: msg.type === 'user' ? 'user' : 'assistant',
                            content: typeof msg.content === 'string' ? msg.content : msg.content?.text || ""
                        }));
                    finalRequestBody.user_input = taskParameters.user_input || textPrompt;
                    finalRequestBody.history = chatMessages.slice(0, chatMessages.findIndex(m => m.role === 'user' && m.content === textPrompt)); // History before current input
                    finalRequestBody.system_prompt = taskParameters.system_prompt || "You are a helpful assistant.";
                    break;
                case "enhance-text":
                    finalApiUrl = "http://localhost:8000/advanced/enhance";
                    finalRequestBody.text = taskParameters.text || textPrompt;
                    finalRequestBody.instruction = taskParameters.instruction || "Improve this text.";
                    break;
                case "file-text-to-answer": 
                    finalApiUrl = "http://localhost:8000/advanced/file-text-to-answer";
                    const visionFormData = new FormData();
                    visionFormData.append('text', taskParameters.text_query || textPrompt || "Describe this content.");
                    if (fileToSubmit) { 
                        visionFormData.append('file', fileToSubmit);
                    } else if (taskParameters.file_id) { 
                        visionFormData.append('file_id', taskParameters.file_id);
                    } else {
                        throw new Error("file-text-to-answer task requires a file or file_id.");
                    }
                    visionFormData.append('model_version', currentAiModel);
                    // Các tham số khác cho vision model
                    visionFormData.append('vision_model_override', taskParameters.vision_model_override || 'gpt-4o');
                    visionFormData.append('assistant_model_override', taskParameters.assistant_model_override || 'gpt-4o');

                    finalRequestBody = visionFormData;
                    finalRequestIsFormData = true;
                    break;
                default:
                    throw new Error(`Tác vụ "${taskKey}" không được hỗ trợ hoặc không xác định.`);
            }

            const finalFetchOptions = {
                method: 'POST',
                headers: {
                    "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
                    'X-User-Email': userInfo.email,
                    'X-User-Role': userInfo.role,
                },
                body: finalRequestIsFormData ? finalRequestBody : JSON.stringify(finalRequestBody)
            };
            if (!finalRequestIsFormData) {
                finalFetchOptions.headers['Content-Type'] = 'application/json';
            }

            const finalResponse = await fetch(finalApiUrl, finalFetchOptions);

            if (!finalResponse.ok) {
                const errorBody = await finalResponse.text();
                throw new Error(`Lỗi API Tác Vụ (${finalResponse.status}): ${errorBody}`);
            }

            let botMessageContent = {};
            if (responseType === 'audio_stream') {
                const blob = await finalResponse.blob();
                botMessageContent = { audio_url: URL.createObjectURL(blob) };
            } else { 
                const data = await finalResponse.json();
                if (taskKey === "text-to-image") {
                    const imageUrl = data.images && data.images.length > 0 ? (data.images[0].url || data.images[0].b64_json) : null;
                    botMessageContent = { image_url: imageUrl ? (imageUrl.startsWith('data:') ? imageUrl : `http://localhost:8000${imageUrl.startsWith('/') ? '' : '/'}${imageUrl}`) : "Lỗi tạo ảnh." };
                } else if (taskKey === "text-to-video") {
                    botMessageContent = { video_url: data.video_url };
                     if (data.task_id && !data.video_url) botMessageContent.text = `Video đang được tạo (Task ID: ${data.task_id}).`; else if (!data.video_url && !data.task_id) botMessageContent.text = "Không nhận được video hoặc Task ID."
                } else if (taskKey === "text-to-code") {
                    botMessageContent = { text: data.code, language: data.language, isCode: true };
                } else if (taskKey === "file-text-to-answer") {
                    botMessageContent = { text: data.answer };
                } else { 
                    botMessageContent = { text: data.answer || data.response || data.text || JSON.stringify(data) };
                }
            }
            setChatHistory(prev => [...prev, { type: 'bot', content: botMessageContent, task: taskKey }]);

        } catch (error) {
            console.error("Lỗi trong handleSubmit:", error);
            // Xóa tin nhắn người dùng nếu có lỗi xảy ra ở bất kỳ bước nào sau khi đã thêm
            setChatHistory(prev => prev.slice(0, prev.length - userMessages.length));
            setChatHistory(prev => [...prev, { type: 'bot', content: { text: `Lỗi: ${error.message}` }, option: "error" }]);
        } finally {
            setIsLoading(false);
            setSelectedFile(null); 
            setImagePreview(null);
            if (genericFileInputRef.current) genericFileInputRef.current.value = null;
            if (imageInputRef.current) imageInputRef.current.value = null;
        }
    };
    
    const renderBotMessageContent = (message) => {
        const content = message.content;
        const task = message.task;

        if (content.audio_url) return <audio controls src={content.audio_url} />;
        if (content.image_url) return <img src={content.image_url} alt="Generated Content" style={{ maxWidth: '100%', maxHeight: '400px', borderRadius: '10px' }} />;
        if (content.video_url && content.video_url.startsWith('blob:')) { // Chỉ hiển thị nếu là blob URL (đã tạo)
            return <video controls width="100%" style={{maxWidth: '500px', borderRadius: '10px'}} src={content.video_url} />;
        }
        if (content.text) {
            if (content.isCode || task === "text-to-code") {
                return <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word', background: '#2d2d2d', color: '#f0f0f0', padding: '10px', borderRadius: '5px' }}><code>{content.text}</code></pre>;
            }
            return <div className="text-response" dangerouslySetInnerHTML={{ __html: content.text.replace(/\n/g, '<br />') }}></div>;
        }
        return "Không có nội dung để hiển thị.";
    };

    return (
        <div className="full-container">
            <div className="sidebar">
                <button className="back-button" onClick={() => navigate('/')}><i className="fa fa-home"></i></button>
                <div className="sidebar_title"><h2>AI Studio</h2></div>

                <div className="choices" style={{padding: '10px'}}>
                    <label htmlFor="aiModelSelect" style={{ color: 'white', marginRight: '10px', display: 'block', marginBottom: '5px' }}>AI Model:</label>
                    <select id="aiModelSelect" className={`options ${isLoading ? 'disabled' : ''}`} value={currentAiModel} onChange={handleAiModelChange} disabled={isLoading} style={{width: '100%', padding: '8px', borderRadius: '4px'}}>
                        {availableAiModels.map(model => (<option key={model.value} value={model.value}>{model.label}</option>))}
                    </select>
                </div>

                <div className="new-chat_btn">
                    <button className={`generate_btn ${isLoading ? 'disabled' : ''}`} onClick={handleNewChat} disabled={isLoading}>
                        + Cuộc trò chuyện mới
                    </button>
                </div>

                <div className="history">
                    <h3 style={{ color: 'white', textAlign: 'center', marginTop: '20px' }}>Lịch sử Chat</h3>
                    <ul className="chat-list" style={{ listStyle: 'none', padding: '0 10px' }}>
                        {conversations.map((conversation) => (
                            <li key={conversation.id}
                                className={`chat-item ${currentConversationId === conversation.id ? 'active' : ''}`}
                                onClick={() => !isLoading && loadConversation(conversation.id)}
                                style={{ 
                                    padding: '10px',
                                    margin: '5px 0',
                                    cursor: isLoading? 'not-allowed' : 'pointer',
                                    background: currentConversationId === conversation.id ? 'linear-gradient(135deg, #3999ff, #50e2ff)' : 'transparent',
                                    color: currentConversationId === conversation.id ? 'black' : 'white',
                                    borderRadius: '5px',
                                    border: currentConversationId !== conversation.id ? '1px solid #444' : 'none',
                                 }}>
                                {conversation.title}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            <div className="content">
                <div className="header_content content-item">
                    {/* --- THÊM LẠI NÚT ADVANCED --- */}
                    <div className="fixed-button-container">
                        <button 
                            className={`rainbow-button fixed-button-advanced ${isLoading ? 'disabled' : ''}`} 
                            onClick={() => !isLoading && navigate('/advanced')} // Điều hướng đến trang advanced
                            disabled={isLoading}
                        >
                            Advanced
                        </button>
                    </div>
                    {/* --- KẾT THÚC THÊM NÚT ADVANCED --- */}
                    <div className="user-info">
                        <i className="fa-solid fa-circle-user fa-2x avatar" style={{color: 'white'}}></i>
                        <span className="username" style={{ color: 'white', marginLeft: '10px' }}>
                            {userInfo.email} ({userInfo.role})
                            {isRateLimited && retryAfter > 0 && <span style={{ color: 'orange', marginLeft: '10px', fontWeight:'bold' }}>Rate Limited! Thử lại sau: {Math.ceil(retryAfter)}s</span>}
                        </span>
                    </div>
                </div>

                <div className="conservation content-item">
                    {chatHistory.map((message, index) => (
                        <div key={index} className={`message ${message.type}-message ${message.content?.video_url ? "video-message" : ""} ${message.content?.audio_url ? "audio-message" : ""} ${message.content?.image_url ? "image-message" : ""}`}>
                            {message.type === 'user' ? (
                                <>
                                    {message.audio_url ? <audio controls src={message.audio_url} /> :
                                     message.video_url ? <video controls src={message.video_url} style={{ width: "100%", maxWidth: "300px", borderRadius: "10px" }} /> :
                                     message.image_url ? <img src={message.image_url} alt={message.fileName || "Ảnh đã gửi"} style={{ maxWidth: "200px", maxHeight: "200px", borderRadius: "10px", border:"1px solid #555" }} /> :
                                     message.content?.startsWith('Đã gửi file:') ? <span style={{fontStyle:'italic', color: '#aaa'}}><i className="fa fa-file-alt" style={{marginRight: '5px'}}></i>{message.content}</span> :
                                     message.content
                                    }
                                </>
                            ) : ( 
                                <>
                                   {renderBotMessageContent(message)}
                                    {(message.content?.audio_url || message.content?.image_url || (message.content?.video_url && message.content?.video_url.startsWith('blob:'))) && ( // Only show share for generated content with direct URLs
                                        <div className="share-buttons" style={{marginTop: '10px', display: 'flex', gap: '10px'}}>
                                            <EmailShareButton url={message.content?.audio_url || message.content?.image_url || message.content?.video_url} subject='Nội dung AI từ Text-To-Everything!' body={`Xem này: ${message.content?.audio_url || message.content?.image_url || message.content?.video_url}`} className='share' style={{color: 'white'}}><EmailIcon size={32} round={true} /></EmailShareButton>
                                            <FacebookShareButton url={message.content?.audio_url || message.content?.image_url || message.content?.video_url} quote="Nội dung AI tuyệt vời!" hashtag='#AICreation'><FacebookIcon size={32} round={true} /></FacebookShareButton>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    ))}
                    {isLoading && <div className="loading-spinner" style={{ margin: '20px auto', width: '50px', height: '50px', borderTopColor: '#3498db', borderLeftColor: '#3498db' }}></div>}
                </div>

                <div className="footer_content content-item">
                    <div id="btn_complex" style={{ position: 'relative', width: '100%', display: 'flex', alignItems: 'center', gap: '10px', padding: '10px', background: '#252525', borderRadius:'8px' }}>
                        
                        <button title="Đính kèm Ảnh" className={`file-input-trigger ${isLoading || isRateLimited ? 'disabled' : ''}`} onClick={() => !isLoading && !isRateLimited && imageInputRef.current?.click()} disabled={isLoading || isRateLimited} style={{background: 'transparent', border:'none', color: '#ccc', fontSize:'20px', cursor:'pointer'}}>
                            <i className="fa fa-image"></i>
                        </button>
                        <input type="file" ref={imageInputRef} onChange={(e) => handleFileSelection(e, 'image')} style={{ display: 'none' }} accept="image/*" />

                        <button title="Đính kèm File (Video, Audio, Doc)" className={`file-input-trigger ${isLoading || isRateLimited ? 'disabled' : ''}`} onClick={() => !isLoading && !isRateLimited && genericFileInputRef.current?.click()} disabled={isLoading || isRateLimited} style={{background: 'transparent', border:'none', color: '#ccc', fontSize:'20px', cursor:'pointer'}}>
                            <i className="fa fa-paperclip"></i>
                        </button>
                        <input type="file" ref={genericFileInputRef} onChange={(e) => handleFileSelection(e, 'generic')} style={{ display: 'none' }} accept=".mp4,.mov,.avi,.mp3,.wav,.m4a,.ogg,.pdf,.doc,.docx,.txt,.md,.csv" />
                        
                        {imagePreview && (
                            <div style={{ position: 'relative', width: '50px', height: '50px', marginLeft: '5px', border: '1px solid #444', borderRadius:'5px' }}>
                                <img src={imagePreview} alt="Xem trước" style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius:'5px' }} />
                                <button onClick={() => { setSelectedFile(null); setImagePreview(null); if (imageInputRef.current) imageInputRef.current.value = null; }}
                                    style={{ position: 'absolute', top: '-5px', right: '-5px', background: 'rgba(255,0,0,0.7)', color: 'white', border: 'none', borderRadius: '50%', width: '18px', height: '18px', cursor: 'pointer', fontSize:'10px', lineHeight:'18px', textAlign:'center', display:'flex', alignItems:'center', justifyContent:'center' }}
                                >X</button>
                            </div>
                        )}
                         {selectedFile && !imagePreview && ( 
                            <div style={{ marginLeft: '5px', color: '#aaa', fontSize: '0.85em', maxWidth: '120px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', display:'flex', alignItems:'center' }} title={selectedFile.name}>
                                <i className="fa fa-file-alt" style={{marginRight: '5px', color:'#777'}}></i>{selectedFile.name}
                                 <button onClick={() => { setSelectedFile(null); if (genericFileInputRef.current) genericFileInputRef.current.value = null; setChatHistory(prev => prev.filter(msg => !(msg.type === 'user' && msg.content?.startsWith('Đã chọn file:'))));}}
                                    style={{ background: 'transparent', color: 'orange', border: 'none', cursor: 'pointer', fontSize:'10px', marginLeft:'5px', padding:'0 2px' }}
                                >X</button>
                            </div>
                        )}

                        <textarea
                            className={`input ${isLoading || isRateLimited ? 'disabled' : ''}`}
                            rows="1" 
                            placeholder="Nhập mô tả, câu hỏi, hoặc nội dung cho AI..."
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey && !isLoading && !isRateLimited) {
                                    e.preventDefault();
                                    handleSubmit();
                                } else if (e.key === 'Enter' && e.shiftKey) {
                                    // Cho phép xuống dòng bằng Shift + Enter
                                }
                            }}
                            disabled={isLoading || isRateLimited}
                            style={{ 
                                flexGrow: 1, 
                                resize: 'none', 
                                minHeight: '40px', 
                                maxHeight: '120px', // Giới hạn chiều cao tối đa
                                padding: '10px',
                                borderRadius: '20px',
                                border: '1px solid #444',
                                background: '#333',
                                color: '#fff',
                                lineHeight: '1.5'
                            }}
                        />
                        <div className="glow-wrapper" style={{marginLeft: '10px'}}>
                            <button id="submit_btn" className={`send-button ${isLoading || isRateLimited ? 'disabled' : ''}`} onClick={handleSubmit} disabled={isLoading || isRateLimited} title="Gửi">
                                <i className="fa fa-paper-plane"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Generate;