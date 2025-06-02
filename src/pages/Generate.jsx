import React, { useState, useEffect, useRef, useCallback } from 'react';
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
    const fileInputRef = useRef(null);

    const [userInfo, setUserInfo] = useState({ email: '', role: 'free', expire: '' });
    const [retryAfter, setRetryAfter] = useState(0);
    const [isRateLimited, setIsRateLimited] = useState(false);
    const [inputValue, setInputValue] = useState('');

    const [selectedApiModel, setSelectedApiModel] = useState("1.0");

    useEffect(() => {
        const fetchUserInfo = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/user-info', {
                    method: "GET",
                    credentials: 'include',
                });
                const data = await response.json();
                if (response.ok && data.email) {
                    localStorage.setItem('email', data.email);
                    setUserInfo({
                        email: data.email,
                        role: data.role || 'free',
                        expire: data.expire || ''
                    });
                    // Tự động chọn model dựa trên role
                    if (data.role === 'pro') { // THAY VIP BẰNG PRO
                        setSelectedApiModel("1.1");
                    } else {
                        setSelectedApiModel("1.0");
                    }
                } else {
                    alert("Không thể lấy thông tin người dùng. Vui lòng đăng nhập lại.");
                    // navigate('/login');
                }
            } catch (error) {
                console.error("Lỗi khi lấy thông tin người dùng:", error);
                alert("Lỗi kết nối khi lấy thông tin người dùng.");
            }
        };
        fetchUserInfo();
    }, [navigate]);

    const commonHeaders = () => ({
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
        'X-User-Email': userInfo.email,
        'X-User-Role': userInfo.role,
    });

    const handleRateLimit = (response) => {
        const retryAfterHeader = response.headers.get('Retry-After');
        const timeToWait = retryAfterHeader ? parseInt(retryAfterHeader, 10) : 60;

        setRetryAfter(timeToWait);
        setIsRateLimited(true);
        alert(`Bạn đã thực hiện quá nhiều yêu cầu. Vui lòng thử lại sau ${timeToWait} giây.`);

        let countdown = timeToWait;
        const timer = setInterval(() => {
            countdown--;
            setRetryAfter(countdown);
            if (countdown <= 0) {
                clearInterval(timer);
                setIsRateLimited(false);
            }
        }, 1000);
    };

    const analyzeTextForModel1_0 = async (textToAnalyze) => {
        setIsLoading(true);
        try {
            const headers = { ...commonHeaders(), "Content-Type": "application/json" };
            // Đảm bảo URL này là endpoint "general analyze" của bạn cho Model 1.0
            const response = await fetch(`http://localhost:8000/analyze`, {
                method: "POST",
                headers: headers,
                body: JSON.stringify({ user_text: textToAnalyze })
            });

            if (response.status === 429) {
                handleRateLimit(response);
                setIsLoading(false);
                return null;
            }
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Lỗi phân tích Model 1.0 (${response.status}): ${errorText}`);
            }
            const data = await response.json();
            return data; // Mong muốn: { intent_analysis: "some_key", parameters: {...} } (parameters có thể có hoặc không)
        } catch (error) {
            console.error("Lỗi khi phân tích (Model 1.0):", error);
            alert(error.message);
            return null;
        } finally {
            // setIsLoading(false); // Sẽ được set ở handleSubmit
        }
    };

    const analyzeAdvancedForModel1_1 = async (text, file) => {
        setIsLoading(true);
        const formData = new FormData();
        if (text) formData.append('text', text);
        if (file) formData.append('file', file);

        try {
            const headers = { ...commonHeaders() };
            const response = await fetch('http://localhost:8000/advanced/analyze', {
                method: 'POST',
                headers: headers,
                body: formData,
            });

            if (response.status === 429) {
                handleRateLimit(response);
                setIsLoading(false);
                return null;
            }
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Lỗi phân tích Model 1.1 (${response.status}): ${errorText}`);
            }
            return await response.json(); // Mong muốn: { task: "sub_api_path", parameters: {...} }
        } catch (error) {
            console.error('Lỗi khi phân tích (Model 1.1):', error);
            alert(error.message);
            return null;
        } finally {
            // setIsLoading(false); // Sẽ được set ở handleSubmit
        }
    };

    const handleFileUploadForModel1_0Plus = async (fileToProcess) => {
        if (userInfo.role !== 'plus') {
             alert("Chức năng này chỉ dành cho tài khoản Plus trở lên.");
             return null;
        }
        setIsLoading(true);
        const fileExtension = fileToProcess.name.split('.').pop().toLowerCase();
        const formData = new FormData();
        formData.append("file", fileToProcess);

        let inputApiUrl;
        let fileTypeBrief;

        if (["mp4", "avi", "mov"].includes(fileExtension)) {
            inputApiUrl = "http://localhost:8000/input/video"; fileTypeBrief = "video";
        } else if (["mp3", "wav"].includes(fileExtension)) {
            inputApiUrl = "http://localhost:8000/input/speech"; fileTypeBrief = "audio";
        } else if (["txt", "doc", "docx", "pdf"].includes(fileExtension)) {
            inputApiUrl = "http://localhost:8000/input/document"; fileTypeBrief = "tài liệu";
        } else if (fileToProcess.type.startsWith('image/')) {
            alert("Để phân tích hình ảnh với Model 1.0 (Plus), vui lòng nhập mô tả kèm theo. Phân tích ảnh trực tiếp nâng cao dành cho Model 1.1 (Pro).");
            setIsLoading(false);
            return { isImageButNeedsText: true }; // Trả về cờ đặc biệt
        }
        else {
            alert("Loại file không được hỗ trợ cho trích xuất nội dung tự động.");
            setIsLoading(false);
            return null;
        }

        try {
            const inputResponse = await fetch(inputApiUrl, {
                method: "POST",
                headers: { ...commonHeaders() },
                body: formData
            });
            if (!inputResponse.ok) throw new Error(`Lỗi trích xuất ${fileTypeBrief} (${inputResponse.status})`);
            
            const data = await inputResponse.json();
            const extractedText = data.text;

            if (!extractedText && extractedText !== "") { // Cho phép empty string nếu file không có text
                alert(`Không trích xuất được nội dung từ ${fileTypeBrief}.`);
                return null;
            }

            const file_url = URL.createObjectURL(fileToProcess);
            let userMessageContent = {
                type: 'user',
                content: `Đã gửi ${fileTypeBrief}: ${fileToProcess.name}. Phân tích nội dung...`,
            };
            if (fileTypeBrief === "video") userMessageContent.video_url = file_url;
            else if (fileTypeBrief === "audio") userMessageContent.audio_url = file_url;
            else userMessageContent.file_url = file_url;
            setChatHistory(prev => [...prev, userMessageContent]);
            
            return await analyzeTextForModel1_0(extractedText || `File ${fileToProcess.name} đã được tải lên.`); // Gửi text trích xuất hoặc thông báo file

        } catch (error) {
            console.error(`Lỗi xử lý file (${fileTypeBrief}):`, error);
            alert(error.message);
            return null;
        } finally {
            // setIsLoading(false); // Sẽ được set ở handleSubmit
        }
    };

    const handleSubmit = async () => {
        const text = inputValue.trim();
        const localSelectedFile = selectedFile;

        if (!text && !localSelectedFile) {
            alert("Vui lòng nhập nội dung hoặc chọn file.");
            return;
        }

        if (userInfo.role === 'free' && selectedApiModel === "1.0" && localSelectedFile) {
            alert("Tài khoản Free không được phép gửi file ở Model 1.0. Vui lòng xóa file hoặc nâng cấp tài khoản.");
            return;
        }

        setIsLoading(true);
        // Xóa input và file ngay sau khi lấy giá trị, trước khi gọi API
        const currentInputValue = inputValue;
        setInputValue('');
        setSelectedFile(null);
        setImagePreview(null);
        if (fileInputRef.current) fileInputRef.current.value = '';

        const userMessages = [];
        if (currentInputValue.trim()) userMessages.push({ type: 'user', content: currentInputValue.trim() });
        if (localSelectedFile && imagePreview) {
            userMessages.push({ type: 'user', image_url: imagePreview, fileName: localSelectedFile.name });
        } else if (localSelectedFile && !imagePreview) { // File không phải ảnh, hoặc ảnh chưa kịp preview
             userMessages.push({ type: 'user', content: `Đã chọn file để xử lý: ${localSelectedFile.name}`, fileObject: localSelectedFile /* Giữ tham chiếu nếu cần */ });
        }
        if (userMessages.length > 0) {
            setChatHistory(prev => [...prev, ...userMessages]);
        }

        try {
            if (selectedApiModel === "1.0") {
                let analysisResult;
                let textForApiCall = currentInputValue.trim();

                if (localSelectedFile && userInfo.role === 'plus') {
                    if (localSelectedFile.type.startsWith('image/')) {
                        // Với ảnh ở Model 1.0 Plus, giả định /analyze có thể nhận file và text
                        // hoặc chúng ta sẽ dùng một intent đặc biệt cho /advanced/file-text-to-answer
                        // Hiện tại, /analyze của user chỉ nhận user_text (JSON).
                        // -> Nên cho /analyze của user nhận FormData (text, file)
                        // Tạm thời, giả định ảnh sẽ được gửi cùng text đến một endpoint phù hợp sau analyze
                        analysisResult = await analyzeTextForModel1_0(textForApiCall || `Hãy mô tả hoặc đặt câu hỏi về hình ảnh ${localSelectedFile.name}.`);
                        // Cần set localSelectedFile để callSpecificApiForModel1_0 biết có file ảnh
                        // (nếu analyzeResult không trực tiếp xử lý nó)
                    } else {
                        // Các loại file khác (audio, video, doc) cho Plus
                        analysisResult = await handleFileUploadForModel1_0Plus(localSelectedFile);
                        // Text for API call có thể là text trích xuất hoặc text gốc người dùng nhập kèm
                        if (analysisResult && analysisResult.extractedText) { // Nếu backend trả về extractedText
                            textForApiCall = analysisResult.extractedText + (textForApiCall ? ` (${textForApiCall})` : '');
                        } else if (analysisResult && analysisResult.isImageButNeedsText) {
                             // Do nothing, alert was shown. Or handle differently.
                             setIsLoading(false); return;
                        }
                    }
                } else {
                    // Chỉ có text (Free/Plus) hoặc Free user (không có file)
                    analysisResult = await analyzeTextForModel1_0(textForApiCall);
                }

                if (analysisResult && analysisResult.intent_analysis) {
                    // Nếu selectedFile là ảnh và intent là image_to_text (hoặc tương tự)
                    // thì truyền selectedFile vào callSpecificApiForModel1_0
                    const fileForSpecificCall = (analysisResult.intent_analysis === 'image_to_text' || analysisResult.intent_analysis === 'ask_about_image') ? localSelectedFile : null;
                    await callSpecificApiForModel1_0(analysisResult.intent_analysis, textForApiCall, analysisResult.parameters, fileForSpecificCall);
                } else if (analysisResult) {
                     alert("Không thể tự động xác định chức năng phù hợp. Vui lòng thử lại hoặc diễn đạt rõ hơn.");
                }

            } else if (selectedApiModel === "1.1" && userInfo.role === 'pro') { // THAY VIP BẰNG PRO
                const analysisResult = await analyzeAdvancedForModel1_1(currentInputValue.trim(), localSelectedFile);
                if (analysisResult && analysisResult.task && analysisResult.parameters) {
                    await callAdvancedApiForModel1_1(analysisResult.task, analysisResult.parameters);
                } else if (analysisResult) {
                     alert("Phân tích nâng cao không thành công hoặc không trả về đủ thông tin.");
                }
            } else {
                alert("Cấu hình model hoặc vai trò người dùng không hợp lệ để thực hiện hành động này.");
            }
        } catch (error) { // Bắt lỗi chung từ các hàm con nếu chúng không tự alert
            console.error("Lỗi không mong muốn trong handleSubmit:", error);
            alert("Đã xảy ra lỗi không mong muốn. Vui lòng thử lại.");
        } finally {
            setIsLoading(false);
        }
    };

    const callSpecificApiForModel1_0 = async (intent, originalText, paramsFromAnalyze = {}, fileToProcess = null) => {
        let apiUrl;
        let requestBody = {};
        let responseType = 'json';
        let botMessageOptionKey = intent;

        const intentToOptionMap = { /* ... giữ nguyên map của bạn ... */ };
        botMessageOptionKey = intentToOptionMap[intent] || intent;

        if (intent === "generate_speech") {
            apiUrl = "http://localhost:8000/text-to-speech";
            requestBody = { text: originalText, voice: paramsFromAnalyze.voice || "banmai", speed: paramsFromAnalyze.speed || "0" };
            responseType = 'blob';
        } else if (intent === "generate_image") {
            apiUrl = "http://localhost:8000/text-to-image/";
            requestBody = { prompt: originalText, steps: paramsFromAnalyze.steps || 0 };
        } else if (intent === "generate_video") {
            apiUrl = "http://localhost:8000/text-to-video";
            requestBody = { prompt: originalText, /* ... */ };
            responseType = 'blob';
        } else if (intent === "generate_text") {
            apiUrl = "http://localhost:8000/chatbot/content";
            requestBody = { prompt: originalText, /* history? */ };
        } else if (intent === "generate_answer") {
            apiUrl = "http://localhost:8000/generate_answer";
            requestBody = { question: originalText, context: paramsFromAnalyze.context };
        } else if (intent === "generate_code") {
            apiUrl = "http://localhost:8000/text-to-code";
            requestBody = { prompt: originalText, language: paramsFromAnalyze.language || 'python' };
        }
        // Xử lý intent cho image_to_text hoặc ask_about_image với fileToProcess
        else if ((intent === "image_to_text" || intent === "ask_about_image") && fileToProcess && fileToProcess.type.startsWith('image/')) {
            // Với Model 1.0 (Plus), nếu backend /analyze không xử lý file trực tiếp,
            // mà trả về intent này, thì frontend sẽ phải gọi /advanced/file-text-to-answer.
            // Điều này cần được backend /analyze của Model 1.0 hỗ trợ bằng cách trả về
            // một "task package" hoặc một intent rõ ràng để frontend biết làm gì.
            // Tạm thời, nếu intent này được trả về, chúng ta sẽ thử gọi /advanced/file-text-to-answer.
            if (userInfo.role === 'plus' || userInfo.role === 'pro') { // Cho phép Plus, Pro
                const formData = new FormData();
                formData.append('text', originalText || `Mô tả hình ảnh này.`);
                formData.append('file', fileToProcess);
                // Thêm các params mặc định cho vision nếu cần
                formData.append('vision_model_override', paramsFromAnalyze.vision_model_override || 'gpt-4o');
                // ...

                apiUrl = 'http://localhost:8000/advanced/file-text-to-answer';
                requestBody = formData;
                responseType = 'formdata_json'; // Cờ đặc biệt
            } else {
                alert("Chức năng phân tích ảnh chi tiết cần tài khoản Plus hoặc Pro.");
                return;
            }
        }
         else {
            alert(`Chức năng cho intent "${intent}" chưa được hỗ trợ hoặc không nhận diện được.`);
            return;
        }

        setIsLoading(true); // Set loading cho từng API call
        try {
            const headers = { ...commonHeaders() };
            if (responseType !== 'formdata_json') {
                headers["Content-Type"] = "application/json";
            }

            const response = await fetch(apiUrl, {
                method: "POST",
                headers: headers,
                body: responseType === 'formdata_json' ? requestBody : JSON.stringify(requestBody)
            });

            if (response.status === 429) { handleRateLimit(response); return; }
            if (!response.ok) throw new Error(`Lỗi API Model 1.0 (${intent} - ${response.status}): ${await response.text()}`);

            let botResponseContent;
            if (responseType === 'blob') {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                if (intent === "generate_speech") botResponseContent = { audio_url: url };
                else if (intent === "generate_video") botResponseContent = { video_url: url };
            } else {
                const data = await response.json();
                if (intent === "generate_image") botResponseContent = { image_url: `http://localhost:8000/${data.image_url}` };
                else if (intent === "generate_text") botResponseContent = { text: data.response };
                else if (intent === "generate_answer") botResponseContent = { text: data.answer };
                else if (intent === "generate_code") botResponseContent = { text: data.code, language: requestBody.language || 'python' };
                else if (responseType === 'formdata_json' && (intent === "image_to_text" || intent === "ask_about_image")) botResponseContent = { text: data.answer };
                else botResponseContent = { text: JSON.stringify(data) };
            }
            setChatHistory(prev => [...prev, { type: 'bot', content: botResponseContent, option: botMessageOptionKey }]);
        } catch (error) {
            console.error(`Lỗi khi gọi API Model 1.0 (${intent}):`, error);
            alert(error.message);
        } finally {
            setIsLoading(false);
        }
    };

    const callAdvancedApiForModel1_1 = async (taskPath, parameters) => {
        const apiUrl = `http://localhost:8000/advanced/${taskPath}`;
        let responseType = 'json';
        if (taskPath === 'text-to-audio') responseType = 'blob';
        // Thêm các trường hợp khác nếu API advanced trả về blob (vd: video từ runwayml)
        // if (taskPath === 'text-to-video' && parameters.model?.includes('runway')) responseType = 'json'; // Runway trả JSON chứa URL


        setIsLoading(true);
        try {
            const headers = { ...commonHeaders(), "Content-Type": "application/json" };
            const response = await fetch(apiUrl, {
                method: "POST",
                headers: headers,
                body: JSON.stringify(parameters)
            });

            if (response.status === 429) { handleRateLimit(response); return; }
            if (!response.ok) {
                 const errorData = await response.json();
                 throw new Error(`Lỗi API Model 1.1 (${taskPath} - ${response.status}): ${errorData.detail || response.statusText}`);
            }

            let botResponseContent;
            if (responseType === 'blob') {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                if (taskPath === 'text-to-audio') botResponseContent = { audio_url: url };
                // else if (taskPath === 'text-to-video-some-blob-model') botResponseContent = { video_url: url };
            } else {
                const data = await response.json();
                if (taskPath === "text-to-image") {
                    botResponseContent = { images_data: data.images || [data] };
                } else if (taskPath === "text-to-code") {
                    botResponseContent = { text: data.code, language: data.language };
                } else if (taskPath === "file-text-to-answer" || taskPath === "generate-answer" ) {
                     botResponseContent = { text: data.answer };
                } else if (taskPath === "chatbot-content") {
                    botResponseContent = { text: data.response };
                } else if (taskPath === "text-to-video") { // RunwayML trả JSON chứa video_url
                    botResponseContent = { video_url: data.video_url, details: data.details };
                }
                else {
                    botResponseContent = { text: data.answer || data.text || data.response || JSON.stringify(data) };
                }
            }
            setChatHistory(prev => [...prev, { type: 'bot', content: botResponseContent, option: `advanced-${taskPath}` }]);
        } catch (error) {
            console.error(`Lỗi khi gọi API Model 1.1 (${taskPath}):`, error);
            alert(error.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleNewChat = () => {
        // ... (Giữ nguyên logic handleNewChat của bạn, hoặcปรับปรุง nếu cần) ...
        if (chatHistory.length > 0 && currentConversationId) {
            const updatedConversations = conversations.map(conv =>
                conv.id === currentConversationId ? { ...conv, messages: chatHistory } : conv
            );
            setConversations(updatedConversations);
        } else if (chatHistory.length > 0 && !currentConversationId) {
             const newConversation = {
                id: Date.now(),
                messages: [...chatHistory],
                title: chatHistory.find(m => m.content && typeof m.content === 'string')?.content?.substring(0, 30) + '...' || "Cuộc trò chuyện mới"
            };
            setConversations(prev => [...prev, newConversation]);
        }
        setChatHistory([]);
        setCurrentConversationId(null);
        setInputValue('');
        setSelectedFile(null);
        setImagePreview(null);
    };

    const loadConversation = (conversationId) => {
        // ... (Giữ nguyên logic loadConversation của bạn, hoặcปรับปรุงnếu cần) ...
        if (chatHistory.length > 0 && currentConversationId && currentConversationId !== conversationId) {
             const currentConvIndex = conversations.findIndex(c => c.id === currentConversationId);
             if (currentConvIndex !== -1) {
                const updatedConversations = [...conversations];
                updatedConversations[currentConvIndex] = { ...updatedConversations[currentConvIndex], messages: chatHistory};
                setConversations(updatedConversations);
             }
        } else if (chatHistory.length > 0 && !currentConversationId) {
            const newConversation = {
                id: Date.now(),
                messages: [...chatHistory],
                title: chatHistory.find(m=>m.content && typeof m.content === 'string')?.content?.substring(0, 30) + '...' || "Cuộc trò chuyện mới"
            };
            setConversations(prev => [...prev, newConversation]);
        }

        const conversationToLoad = conversations.find(c => c.id === conversationId);
        if (conversationToLoad) {
            setChatHistory(conversationToLoad.messages);
            setCurrentConversationId(conversationId);
        }
    };
    
    const handleFileFromInput = (event) => {
        const file = event.target.files[0];
        if (file) {
            if (userInfo.role === 'free' && selectedApiModel === "1.0") {
                alert("Tài khoản Free không được phép tải file lên ở Model 1.0.");
                if (fileInputRef.current) fileInputRef.current.value = '';
                return;
            }
            setSelectedFile(file);
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onloadend = () => setImagePreview(reader.result);
                reader.readAsDataURL(file);
            } else {
                setImagePreview(null);
            }
        }
    };

    const renderBotMessageContent = (message) => {
        if (!message.content) return "Lỗi: Nội dung không xác định";
        const content = message.content;

        if (content.audio_url) return <audio controls src={content.audio_url} />;
        if (content.video_url) return <video controls width="100%" style={{ maxWidth: "500px", borderRadius: "10px" }} src={content.video_url} />;
        if (content.image_url) return <img src={content.image_url} alt="Generated" style={{ maxWidth: '100%', borderRadius: '10px' }} />;
        if (content.images_data) {
            return content.images_data.map((imgData, idx) => (
                <div key={idx} style={{ marginBottom: '10px' }}>
                    <img src={imgData.url || `data:image/png;base64,${imgData.b64_json}`} alt={`Generated ${idx + 1}`} style={{ maxWidth: '100%', borderRadius: '10px' }} />
                    {imgData.revised_prompt && <p style={{ fontSize: '0.8em', color: '#ccc' }}>Revised Prompt: {imgData.revised_prompt}</p>}
                </div>
            ));
        }
        if (content.file_url) return <a href={content.file_url} download={content.name || "download"} target="_blank" rel="noopener noreferrer" className="file-link">📄 Tải File</a>;
        
        if (content.text) {
            const langClass = content.language ? `language-${content.language}` : '';
             if (message.option === 'advanced-text-to-code' || message.option === '8' || (typeof content.text === 'string' && (content.text.includes('def ') || content.text.includes('function(')))) {
                 return <pre className={langClass} style={{ whiteSpace: 'pre-wrap', background: '#2d2d2d', padding: '10px', borderRadius: '5px', color: '#ccc', maxHeight:'300px', overflowY:'auto' }}><code>{content.text}</code></pre>;
            }
            return <div className="text-response" style={{whiteSpace: 'pre-wrap'}}>{content.text}</div>;
        }
        if (content.details && content.video_url) { // For runwayml text-to-video
            return (
                <div>
                    <p>Video đang được xử lý hoặc đã hoàn thành. Kiểm tra URL nếu có.</p>
                    {content.details.status && <p>Trạng thái: {content.details.status}</p>}
                </div>
            );
        }
        return <div style={{whiteSpace: 'pre-wrap'}}>{typeof content === 'object' ? JSON.stringify(content, null, 2) : content}</div>;
    };

    return (
        <div className="full-container">
            <div className="sidebar">
                <button className="back-button" onClick={() => navigate('/')}><i className="fa fa-home"></i></button>
                <div className="sidebar_title"><h2>Menu</h2></div>
                <div className="choices" style={{ padding: '10px' }}>
                    <label htmlFor="api-model-select" style={{ color: 'white', marginRight: '10px', display:'block', marginBottom:'5px' }}>Model API:</label>
                    <select
                        id="api-model-select"
                        className={`options ${isLoading ? 'disabled' : ''}`}
                        value={selectedApiModel}
                        onChange={(e) => {
                            if (e.target.value === "1.1" && userInfo.role !== 'pro') { // THAY VIP BẰNG PRO
                                alert("Model 1.1 (Advanced) chỉ dành cho tài khoản Pro.");
                                return;
                            }
                            setSelectedApiModel(e.target.value);
                        }}
                        disabled={isLoading || (userInfo.role !== 'pro' && selectedApiModel === "1.1" && e.target.value === "1.1")} // Chỉnh sửa logic disabled
                    >
                        <option value="1.0">Model 1.0 (Standard)</option>
                        { /* Chỉ hiển thị option 1.1 nếu user là Pro */ }
                        <option value="1.1" disabled={userInfo.role !== 'pro'}>Model 1.1 (Advanced Pro)</option>
                    </select>
                    <p style={{color: 'white', fontSize: '0.8em', marginTop: '5px'}}>
                        {selectedApiModel === "1.0" ? 
                         (userInfo.role === 'free' ? "Role: Free (Giới hạn, không gửi file)" : `Role: ${userInfo.role === 'plus' ? 'Plus' : userInfo.role} (Standard)`)
                         : `Role: Pro (API Nâng cao)`}
                    </p>
                </div>
                <div className="new-chat_btn">
                    <button className={`generate_btn ${isLoading ? 'disabled' : ''}`} onClick={handleNewChat} disabled={isLoading}>
                        + Cuộc trò chuyện mới
                    </button>
                </div>
                <div className="history">
                    <ul className="chat-list" style={{ listStyle: 'none', padding: 0 }}>
                        {conversations.map((conversation) => (
                            <li key={conversation.id}
                                className={`chat-item ${currentConversationId === conversation.id ? 'active' : ''}`}
                                onClick={() => !isLoading && loadConversation(conversation.id)}
                                style={{ /* ... style cũ ... */ cursor: isLoading? 'not-allowed' : 'pointer' }}
                            >
                                {conversation.title}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            <div className="content">
                <div className="header_content content-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                     <div style={{display: 'flex', alignItems: 'center'}}>
                        <div className="user-info" style={{marginRight: '20px'}}>
                            <i className="fa-solid fa-circle-user fa-2x avatar"></i>
                            <span className="username" style={{marginLeft: '10px', color: 'white'}}>{userInfo.email} ({userInfo.role})</span>
                        </div>
                        {isRateLimited && <span style={{color: 'red', marginLeft:'10px'}}>Thử lại sau: {retryAfter}s</span>}
                    </div>
                    {/* KHÔI PHỤC NÚT ADVANCED */}
                    <div className="fixed-button-container">
                        <button 
                            className={`rainbow-button fixed-button-advanced ${isLoading ? 'disabled' : ''}`} 
                            onClick={() => navigate('/advanced')} // Điều hướng đến trang /advanced
                            disabled={isLoading}
                        >
                            Advanced
                        </button>
                    </div>
                </div>

                <div className="conservation content-item">
                    {chatHistory.map((message, index) => (
                        <div key={index} className={`message ${message.type}-message`}>
                            {message.type === 'user' ? (
                                <div className="user-message-bubble">
                                    {message.image_url && <img src={message.image_url} alt={message.fileName || "Ảnh đã gửi"} style={{ maxWidth: "200px", maxHeight:"200px", borderRadius: "10px", marginBottom:'5px', display:'block' }} />}
                                    {message.audio_url && <audio controls src={message.audio_url} style={{marginBottom:'5px', display:'block'}}/>}
                                    {message.video_url && <video controls src={message.video_url} style={{ maxWidth: "300px", maxHeight:"200px", borderRadius: "10px", marginBottom:'5px', display:'block' }}/>}
                                    {message.file_url && <a href={message.file_url} download={message.fileName || "file"} target="_blank" rel="noopener noreferrer" className="file-link" style={{display:'block', marginBottom:'5px'}}>📄 {message.fileName || "Đã gửi file"}</a>}
                                    {message.content && <div style={{whiteSpace: 'pre-wrap'}}>{message.content}</div>}
                                </div>
                            ) : (
                                <div className="bot-message-bubble">
                                    {renderBotMessageContent(message)}
                                </div>
                            )}
                        </div>
                    ))}
                    {isLoading && <div className="loading-spinner" style={{margin: '20px auto'}}></div>}
                </div>

                <div className="footer_content content-item">
                    <div id="btn_complex" style={{ position: 'relative', width: '100%', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <button
                            className={`file-upload-btn-footer ${isLoading || (selectedApiModel === "1.0" && userInfo.role === 'free') ? 'disabled' : ''}`}
                            onClick={() => !(selectedApiModel === "1.0" && userInfo.role === 'free') && fileInputRef.current?.click()}
                            disabled={isLoading || (selectedApiModel === "1.0" && userInfo.role === 'free')}
                            title={ (selectedApiModel === "1.0" && userInfo.role === 'free') ? "Tài khoản Free không thể gửi file" : "Đính kèm file (ảnh, audio, video, tài liệu)"}
                            style={{ padding: '10px', borderRadius:'50%', width:'40px', height:'40px', flexShrink:0, cursor: (selectedApiModel === "1.0" && userInfo.role === 'free') ? 'not-allowed' : 'pointer' }}
                        >
                            📎
                        </button>
                        <input
                            type="file" ref={fileInputRef} onChange={handleFileFromInput}
                            style={{ display: 'none' }}
                            accept="image/*,audio/*,video/*,.pdf,.doc,.docx,.txt"
                        />
                         {imagePreview && (
                            <div style={{ position: 'relative', flexShrink:0 }}>
                                <img src={imagePreview} alt="Preview" style={{ width: '40px', height: '40px', borderRadius: '4px', objectFit: 'cover' }} />
                                <button onClick={() => { setImagePreview(null); setSelectedFile(null); if(fileInputRef.current) fileInputRef.current.value = ''; }}
                                    style={{ position: 'absolute', top: '-5px', right: '-5px', background: 'rgba(0,0,0,0.6)', color: 'white', border: 'none', borderRadius: '50%', width: '18px', height: '18px', cursor: 'pointer', fontSize:'10px', lineHeight:'18px', padding:0, display:'flex', alignItems:'center', justifyContent:'center' }}
                                >×</button>
                            </div>
                        )}
                        <textarea
                            className={`input ${isLoading ? 'disabled' : ''}`}
                            rows="1"
                            placeholder="Nhập yêu cầu của bạn ở đây..."
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); if (!isLoading) handleSubmit(); }}}
                            disabled={isLoading}
                            style={{ flexGrow: 1, resize: 'none', minHeight:'40px', borderRadius:'20px', padding:'10px 15px' }}
                        />
                        <button
                            id="submit_btn_main"
                            className={`glow-wrapper ${isLoading ? 'disabled' : ''}`}
                            onClick={() => !isLoading && handleSubmit()}
                            disabled={isLoading}
                            style={{padding:'10px 20px', borderRadius:'20px', marginLeft:'5px', flexShrink:0}}
                        >
                            Gửi
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Generate;