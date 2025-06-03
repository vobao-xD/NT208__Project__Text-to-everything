import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Cookies from "js-cookie";

import {
    EmailShareButton,
    EmailIcon,
    FacebookShareButton,
    FacebookIcon
} from "react-share";

import FileUpload from '../components/FileUpload';
import { toast, ToastContainer, Slide } from 'react-toastify';
import { BadgeCheck, CircleAlert, Info, TriangleAlert } from 'lucide-react';

const Generate = () => {
    const navigate = useNavigate();
    const [chatHistory, setChatHistory] = useState([]);
    const [selectedOption, setSelectedOption] = useState("0");
    const [conversations, setConversations] = useState([]);
    const [currentConversationId, setCurrentConversationId] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isManualSelection, setIsManualSelection] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const fileInputRef = useRef(null);
    const imageInputRef = useRef(null);
    const [userInfo, setUserInfo] = useState({ email: ' ', role: 'free', expire: ' ' });
    const [retryAfter, setRetryAfter] = useState(0);
    const [isRateLimited, setIsRateLimited] = useState(false);
    const [inputValue, setInputValue] = useState('');
    const [role, setRole] = useState('');
    const [selectedMode, setSelectedMode] = useState("1");
    const [showFunctionDropdown, setShowFunctionDropdown] = useState(false);
    const [isManualMode, setIsManualMode] = useState(false);
    const generatorIdMap = {
        "1": "01010101-0101-0101-0101-010101010101",
        "2": "22222222-2222-2222-2222-222222222222",
        "3": "33333333-3333-3333-3333-333333333333",
        "4": "",
        "5": "55555555-5555-5555-5555-555555555555",
        "6": "66666666-6666-6666-6666-666666666666",
        "7": "77777777-7777-7777-7777-777777777777",
        "8": "88888888-8888-8888-8888-888888888888",
        "9": "99999999-9999-9999-9999-999999999999",
        "10": "10101010-1010-1010-1010-101010101010",
        "11": "11111111-1111-1111-1111-111111111111"
    }

    // Tạo map ngược lại từ UUID sang option
    const reverseGeneratorIdMap = Object.entries(generatorIdMap).reduce((acc, [key, value]) => {
        if (value) { // Chỉ thêm vào map nếu value không rỗng
            acc[value] = key;
        }
        return acc;
    }, {});

    // Hàm chuyển đổi từ UUID sang option
    const getOptionFromGeneratorId = (generatorId) => {
        return reverseGeneratorIdMap[generatorId] || "0"; // Trả về "0" nếu không tìm thấy
    };

    useEffect(() => {
        const init = async () => {
            try {
                console.log("Cookies:", document.cookie);
                const res1 = await fetch('http://localhost:8000/api/user-info', {
                    method: "GET",
                    credentials: 'include',
                });
                const data1 = await res1.json();
                if (!data1.email) {
                    alert("Không tìm thấy email!");
                    toast.error("Không tìm thấy email!", {
                        closeButton: true,
                        className: 'p-0 w-[400px] border border-red-600/40 backdrop-blur-lg',
                        ariaLabel: 'Error',
                    })
                    return;
                }
                localStorage.setItem("email", data1.email);
                fetchChatHistories();
                const res2 = await fetch(`http://localhost:8000/user-subscription?email=${data1.email}`);
                const data2 = await res2.json();
                localStorage.setItem("role", data2.role);
                localStorage.setItem("billingCycle", data2.billingCycle || "monthly");

                // Chỉ set role state sau khi đã lấy và lưu role vào localStorage
                setRole(data2.role);
            } catch (err) {
                console.error("Lỗi khi khởi tạo:", err);
            }
        };

        init();
    }, [navigate]);

    const detectInputFileType = (filename) => {
        const ext = filename.split(".").pop().toLowerCase();
        if (["mp3", "wav"].includes(ext)) return "audio";
        if (["mp4", "avi", "mov"].includes(ext)) return "video";
        if (["pdf", "txt", "doc", "docx"].includes(ext)) return "file";
        return "file";
    };

    const normalizeBotMessageContent = (botMessage) => {
        // Xử lý đặc biệt cho output text của code generation
        let outputText = null;
        if (botMessage.option === "8") {
            outputText = typeof botMessage.content.text === 'object' ?
                JSON.stringify(botMessage.content.text) :
                botMessage.content.text;
        } else {
            outputText = botMessage.content.text || null;
        }

        return {
            type: botMessage.content.image_url
                ? "image"
                : botMessage.content.video_url
                    ? "video"
                    : botMessage.content.audio_url
                        ? "audio"
                        : "text",
            text: outputText,
            image_url: botMessage.content.image_url || null,
            video_url: botMessage.content.video_url || null,
            audio_url: botMessage.content.audio_url || null,
        };
    };

    const prepareChatDetailPayload = (inputText, inputFileName, normalizedContent, generatorId) => {
        return {
            input: {
                text: inputFileName ? null : inputText,
                file: inputFileName,
            },
            input_type: inputFileName ? detectInputFileType(inputFileName) : "text",
            output: normalizedContent,
            generator_id: generatorId,
        };
    };

    const addChatDetail = async (payload) => {
        try {
            const token = Cookies.get('access_token');
            if (!token) {
                toast.error("Không tìm thấy token xác thực", {
                    closeButton: true,
                    className: 'p-0 w-[400px] border border-red-600/40 backdrop-blur-lg',
                    ariaLabel: 'Error',
                });
                return;
            }

            if (!currentConversationId) {
                // Nếu chưa có conversation, tạo mới
                const newChatResponse = await fetch("http://127.0.0.1:8000/chat-history", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        details: []
                    })
                });

                if (!newChatResponse.ok) {
                    throw new Error(`Lỗi tạo cuộc trò chuyện mới: ${await newChatResponse.text()}`);
                }

                const newChatData = await newChatResponse.json();
                setCurrentConversationId(newChatData.id);
            }

            // Lấy UUID tương ứng với option từ generatorIdMap
            const generatorId = generatorIdMap[payload.generator_id];
            if (!generatorId) {
                throw new Error(`Không tìm thấy generator_id cho option ${payload.generator_id}`);
            }

            // Chuẩn bị payload dựa trên input_type
            const chatDetailPayload = {
                input_type: payload.input_type,
                text_prompt: payload.input.text || null,
                input_file_name: payload.input.file || null,
                output_type: payload.output.type,
                output_text: payload.output.text || null,
                output_url: payload.output.audio_url || payload.output.image_url || payload.output.video_url || null,
                generator_id: generatorId
            };

            console.log("Sending chat detail:", chatDetailPayload);

            const response = await fetch(
                `http://127.0.0.1:8000/chat-history/${currentConversationId}/add-detail`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`,
                    },
                    body: JSON.stringify(chatDetailPayload),
                }
            );

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Lỗi lưu chi tiết chat: ${errorText}`);
            }

            const savedDetail = await response.json();
            console.log("Saved chat detail:", savedDetail);

            // Cập nhật lại danh sách conversations mà không thay đổi tiêu đề
            const updatedConversations = await fetch("http://127.0.0.1:8000/chat-history", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                }
            }).then(res => res.json());

            setConversations(updatedConversations.map(c => {
                // Giữ nguyên tiêu đề từ conversation hiện tại nếu đã có
                const existingConversation = conversations.find(existing => existing.id === c.id);
                const title = existingConversation ? existingConversation.title :
                    (c.details[0]?.text_prompt || "Cuộc trò chuyện mới").substring(0, 30) + '...';

                return {
                    id: c.id,
                    title: title,
                    messages: c.details
                };
            }));

        } catch (err) {
            console.error("addChatDetail error:", err);
            toast.error("Có lỗi xảy ra khi lưu chi tiết chat: " + err.message, {
                closeButton: true,
                className: 'p-0 w-[400px] border border-red-600/40 backdrop-blur-lg',
                ariaLabel: 'Error',
            });
        }
    };

    const handleNewChat = async () => {
        try {
            const token = Cookies.get('access_token');
            if (!token) {
                toast.error("Không tìm thấy token xác thực", {
                    closeButton: true,
                    className: 'p-0 w-[400px] border border-red-600/40 backdrop-blur-lg',
                    ariaLabel: 'Error',
                });
                return;
            }

            const response = await fetch("http://127.0.0.1:8000/chat-history", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    details: []
                })
            });

            if (!response.ok) {
                throw new Error(`Lỗi API (${response.status}): ${await response.text()}`);
            }

            const data = await response.json();
            const conversation_id = data.id;

            if (chatHistory.length > 0) {
                // Lấy prompt đầu tiên từ chat history
                const firstPrompt = chatHistory[0].content;
                const title = firstPrompt.length > 30 ? firstPrompt.substring(0, 30) + '...' : firstPrompt;

                const newConversation = {
                    id: conversation_id,
                    messages: [...chatHistory],
                    title: title
                };
                setConversations(prev => [...prev, newConversation]);
            }

            setCurrentConversationId(conversation_id);
            setChatHistory([]);
        } catch (error) {
            console.error("Error:", error);
            toast.error("Có lỗi xảy ra khi tạo cuộc trò chuyện mới: " + error.message, {
                closeButton: true,
                className: 'p-0 w-[400px] border border-red-600/40 backdrop-blur-lg',
                ariaLabel: 'Error',
            });
        }
    };

    const fetchChatHistories = async () => {
        try {
            const token = Cookies.get('access_token');
            if (!token) {
                console.error("Không tìm thấy token xác thực");
                return;
            }

            const response = await fetch("http://127.0.0.1:8000/chat-history", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error(`Lỗi API (${response.status}): ${await response.text()}`);
            }

            const data = await response.json();
            setConversations(data.map(c => {
                // Lấy prompt đầu tiên từ details
                const firstPrompt = c.details[0]?.text_prompt || "Cuộc trò chuyện mới";
                const title = firstPrompt.length > 30 ? firstPrompt.substring(0, 30) + '...' : firstPrompt;

                return {
                    id: c.id,
                    title: title,
                    messages: c.details
                };
            }));
        } catch (err) {
            console.error("fetchChatHistories error:", err);
            toast.error("Có lỗi xảy ra khi tải lịch sử chat: " + err.message, {
                closeButton: true,
                className: 'p-0 w-[400px] border border-red-600/40 backdrop-blur-lg',
                ariaLabel: 'Error',
            });
        }
    };

    const loadConversation = async (conversationId) => {
        try {
            const token = Cookies.get('access_token');
            if (!token) {
                toast.error("Không tìm thấy token xác thực", {
                    closeButton: true,
                    className: 'p-0 w-[400px] border border-red-600/40 backdrop-blur-lg',
                    ariaLabel: 'Error',
                });
                return;
            }

            const response = await fetch(`http://127.0.0.1:8000/chat-history/${conversationId}`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error(`Lỗi API (${response.status}): ${await response.text()}`);
            }

            const data = await response.json();
            console.log("Data from API:", data);

            const messages = [];

            for (let detail of data.details) {
                // USER MESSAGE
                const userMsg = {
                    type: "user",
                    content: detail.text_prompt || `[Đã gửi tệp: ${detail.input_file_name}]`,
                };

                if (detail.input_type === "audio") {
                    userMsg.audio_url = detail.input_file_url;
                } else if (detail.input_type === "video") {
                    userMsg.video_url = detail.input_file_url;
                } else if (detail.input_type === "image") {
                    userMsg.image_url = detail.input_file_url;
                } else if (detail.input_type === "file") {
                    userMsg.file_url = detail.input_file_url;
                }

                messages.push(userMsg);

                // BOT MESSAGE
                const botMsg = {
                    type: "bot",
                    content: {},
                    option: getOptionFromGeneratorId(detail.generator_id)
                };

                if (detail.output_text) {
                    botMsg.content.text = detail.output_text;
                }

                const outputUrl = detail.output_url;
                const outputType = detail.output_type;

                if (outputUrl) {
                    if (outputType === "audio" || botMsg.option === "1" || botMsg.option === "9") {
                        botMsg.content.audio_url = outputUrl;
                    } else if (outputType === "video" || botMsg.option === "3" || botMsg.option === "10") {
                        botMsg.content.video_url = outputUrl;
                    } else if (outputType === "image" || botMsg.option === "2" || botMsg.option === "5") {
                        if (detail.generator_id === generatorIdMap["5"]) {
                            botMsg.content.improved_image_url = outputUrl;
                        } else {
                            botMsg.content.image_url = outputUrl;
                        }
                    }
                }

                messages.push(botMsg);
            }

            setChatHistory(messages);
            setCurrentConversationId(conversationId);
        } catch (err) {
            console.error("loadConversation error:", err);
            toast.error("Có lỗi xảy ra khi tải cuộc trò chuyện: " + err.message, {
                closeButton: true,
                className: 'p-0 w-[400px] border border-red-600/40 backdrop-blur-lg',
                ariaLabel: 'Error',
            });
        }
    };

    const handleDeleteConversation = async (conversationId) => {
        const confirmDelete = window.confirm("Bạn có chắc chắn muốn xoá đoạn chat này?");
        if (!confirmDelete) return;

        try {
            const token = Cookies.get('access_token');
            if (!token) {
                toast.error("Không tìm thấy token xác thực", {
                    closeButton: true,
                    className: 'p-0 w-[400px] border border-red-600/40 backdrop-blur-lg',
                    ariaLabel: 'Error',
                });
                return;
            }

            const response = await fetch(`http://127.0.0.1:8000/chat-history/${conversationId}`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error(`Lỗi API (${response.status}): ${await response.text()}`);
            }

            setConversations(prev => prev.filter(c => c.id !== conversationId));
            if (conversationId === currentConversationId) {
                setChatHistory([]);
                setCurrentConversationId(null);
            }
        } catch (err) {
            console.error("Xoá chat lỗi:", err);
            toast.error("Có lỗi xảy ra khi xoá cuộc trò chuyện: " + err.message, {
                closeButton: true,
                className: 'p-0 w-[400px] border border-red-600/40 backdrop-blur-lg',
                ariaLabel: 'Error',
            });
        }
    };

    const handleModeChange = (e) => {
        const newMode = e.target.value;
        if (newMode === "1.1" && role !== "pro") {
            toast.error("Chỉ tài khoản Pro mới được phép sử dụng chế độ 1.1. Vui lòng nâng cấp lên Pro để sử dụng tính năng này!", {
                closeButton: true,
                onClose: () => navigate('/advanced')
            });
            return;
        }
        setSelectedMode(newMode);
    };

    const handleAutoAnalyze = async (text) => {
        try {
            const response = await fetch("http://127.0.0.1:8000/analyze", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
                    'X-User-email': localStorage.getItem("email"),
                    'X-User-role': role
                },
                body: JSON.stringify({ user_text: text })
            });
            if (response.status === 429) {
                console.log("Rate limit exceeded");
                const data = await response.json();
                const retryAfter = response.headers.get('Retry-After');
                const timeToWait = retryAfter ? parseInt(retryAfter, 10) * 1000 : 5000;

                setRetryAfter(timeToWait);
                setIsRateLimited(true);
                toast.error("hết lượt miễn phí. Vui lòng thử laị sau.");
                let timer = setInterval(() => {
                    setRetryAfter(prev => {
                        if (prev <= 1) {
                            clearInterval(timer);
                            setIsRateLimited(false);
                            return 0;
                        }
                        return prev - 1;
                    });
                }, 1000);
            }
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Lỗi API (${response.status}): ${errorText}`);
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

            if (data.intent_analysis && actionMap[data.intent_analysis]) {
                const selectedAction = actionMap[data.intent_analysis];

                // Kiểm tra quyền trước khi set option
                if (selectedAction === "3" && role !== "pro") {
                    toast.error("Chỉ tài khoản Pro mới được phép sử dụng chức năng Text to Video. Vui lòng nâng cấp lên Pro để sử dụng tính năng này!", {
                        closeButton: true,
                        onClose: () => navigate('/advanced')
                    });
                    return {
                        success: false
                    };
                }

                return {
                    success: true,
                    intent_analysis: data.intent_analysis,
                    prompt: text,
                    action: selectedAction
                };
            }

            // Fallback khi không phân tích được
            setShowFunctionDropdown(true);
            toast.error("Không thể phân tích yêu cầu của bạn. Vui lòng chọn chức năng thủ công.", {
                closeButton: true,
                className: 'p-0 w-[400px] border border-red-600/40',
                ariaLabel: 'Error',
            });
            return {
                success: false,
                error: "Không thể phân tích yêu cầu"
            };
        } catch (error) {
            console.error("Lỗi khi phân tích:", error);
            setShowFunctionDropdown(true);
            return {
                success: false,
                error: error.message
            };
        }
    };

    const handleFileSelect = (event) => {
        if (role === "free") {
            alert("Tài khoản miễn phí không được phép upload. Vui lòng nâng cấp lên Plus hoặc Pro để sử dụng tính năng này!");
            navigate('/advanced');
            return;
        }
        const file = event.target.files[0];
        if (file) {
            setSelectedFile(file);
            handleFileUpload(file);
        }
    };

    const handleFileUpload = async (file) => {
        if (role === "free") {
            alert("Tài khoản miễn phí không được phép upload. Vui lòng nâng cấp lên Plus hoặc Pro để sử dụng tính năng này!");
            navigate('/advanced');
            return;
        }
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

    const handleImageSelect = (event) => {
        if (role === "free") {
            alert("Tài khoản miễn phí không được phép upload. Vui lòng nâng cấp lên Plus hoặc Pro để sử dụng tính năng này!");
            navigate('/advanced');
            return;
        }
        const file = event.target.files[0];
        if (file && file.type.startsWith('image/')) {
            setSelectedFile(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setImagePreview(reader.result);
            };
            reader.readAsDataURL(file);
        } else {
            alert('Vui lòng chọn file ảnh');
        }
    };

    const handleSubmit = async (text, file = null) => {
        if (!text.trim()) {
            toast.error("Vui lòng nhập nội dung trước khi gửi.", {
                closeButton: true,
                className: 'p-0 w-[400px] border border-red-600/40 backdrop-blur-lg',
                ariaLabel: 'Error',
            })
            return;
        }

        setIsLoading(true);
        setSelectedFile(file);

        const inputType = file ? detectInputFileType(file.name) : "text";
        const fileName = file ? file.name : null;
        const finalText = file ? "" : text;

        // Nếu có cả text và file ảnh, lưu thành 2 message riêng biệt
        if (selectedFile && imagePreview) {
            setChatHistory(prev => [
                ...prev,
                { type: 'user', content: text },
                { type: 'user', image_url: imagePreview }
            ]);
        } else {
            // Nếu chỉ có text hoặc chỉ có ảnh
            if (imagePreview) {
                setChatHistory(prev => [...prev, { type: 'user', image_url: imagePreview }]);
            } else {
                setChatHistory(prev => [...prev, { type: 'user', content: text }]);
            }
        }

        try {
            let finalText = text;
            let currentOption = selectedOption;

            // Nếu có file ảnh được chọn
            if (selectedFile) {
                const formData = new FormData();
                formData.append('text', finalText);
                formData.append('file', selectedFile);
                formData.append('vision_model_override', 'gpt-4o');
                formData.append('detail_vision', 'auto');
                formData.append('max_tokens_vision', '300');
                formData.append('assistant_model_override', 'gpt-4o');

                const response = await fetch('http://localhost:8000/advanced/file-text-to-answer', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`Lỗi API (${response.status}): ${await response.text()}`);
                }

                const data = await response.json();
                const botMessage = {
                    type: 'bot',
                    content: { text: data.answer },
                    option: "12"
                };
                setChatHistory(prev => [...prev, botMessage]);

                // Reset về Auto Analyze sau khi xử lý xong
                setSelectedOption("0");

                // Reset file và preview
                setSelectedFile(null);
                setImagePreview(null);
                if (fileInputRef.current) {
                    fileInputRef.current.value = '';
                }
                if (imageInputRef.current) {
                    imageInputRef.current.value = '';
                }

                setIsLoading(false);
                return;
            }

            // Nếu đang ở chế độ Auto Analyze
            if (selectedOption === "0" && !file) {
                const analyzeResult = await handleAutoAnalyze(text);
                if (analyzeResult.success) {
                    currentOption = analyzeResult.action;
                    finalText = analyzeResult.prompt;
                    setChatHistory((prev) => [
                        ...prev,
                        {
                            type: "bot",
                            content: {
                                text: `[AutoAnalyze đã xác định chức năng phù hợp]`,
                            },
                            option: "0",
                        },
                    ]);
                } else {
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

            // Xử lý API URL dựa trên mode và role
            if (currentOption === "1") {
                apiUrl = selectedMode === "1.1" && role === "pro" ? "http://127.0.0.1:8000/advanced/text-to-speech" : "http://127.0.0.1:8000/text-to-speech";
                requestBody = {
                    text: finalText,
                    voice: "banmai",
                    speed: "0"
                };
            } else if (currentOption === "2") {
                if (selectedMode === "1.1" && role === "pro") {
                    apiUrl = "http://127.0.0.1:8000/advanced/text-to-image";
                    requestBody = {
                        prompt: finalText,
                        n: 1,
                        size: "1024x1024",
                        quality: "standard",
                        style: "vivid",
                        response_format: "url"
                    };
                } else {
                    apiUrl = "http://127.0.0.1:8000/text-to-image";
                    requestBody = {
                        prompt: finalText,
                        steps: 0
                    };
                }
            } else if (currentOption === "3") {
                apiUrl = "http://127.0.0.1:8000/text-to-video";
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
                if (selectedMode === "1.1" && role === "pro") {
                    apiUrl = "http://127.0.0.1:8000/advanced/chatbot-content";
                    requestBody = {
                        user_input: finalText,
                        history: [],
                        system_prompt: "You are a helpful and friendly chatbot.",
                        max_tokens: 500
                    };
                } else {
                    apiUrl = "http://127.0.0.1:8000/chatbot/content";
                    requestBody = {
                        prompt: finalText
                    };
                }
            } else if (currentOption === "7") {
                if (selectedMode === "1.1" && role === "pro") {
                    apiUrl = "http://127.0.0.1:8000/advanced/generate-answer";
                    requestBody = {
                        question: finalText,
                        context: "string",
                        max_tokens: 500
                    };
                } else {
                    apiUrl = "http://127.0.0.1:8000/generate_answer";
                    requestBody = {
                        question: finalText
                    };
                }
            } else if (currentOption === "8") {
                if (selectedMode === "1.1" && role === "pro") {
                    apiUrl = "http://127.0.0.1:8000/advanced/text-to-code";
                    requestBody = {
                        prompt: finalText,
                        language: "python",
                        max_tokens: 150
                    };
                } else {
                    apiUrl = "http://127.0.0.1:8000/text-to-code";
                    requestBody = {
                        prompt: finalText
                    };
                }
            } else {
                toast.error("Tính năng này chưa được hỗ trợ!", {
                    closeButton: true,
                    className: 'p-0 w-[400px] border border-red-600/40',
                    ariaLabel: 'Error',
                });
                setIsLoading(false);
                return;
            }

            const response = await fetch(apiUrl, {
                method: "POST",
                headers: headers,
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                throw new Error(`Lỗi API (${response.status}): ${await response.text()}`);
            }

            let botMessage = { type: "bot", content: {}, option: currentOption };
            if (currentOption === "3") {
                const blob = await response.blob();
                botMessage.content.video_url = URL.createObjectURL(blob);
            } else {
                const data = await response.json();
                if (currentOption === "1") { // Text to Speech
                    console.log("Text to Speech response:", data); // Debug log
                    botMessage = {
                        type: 'bot',
                        content: {
                            audio_url: data.audio_url
                        },
                        option: currentOption
                    };
                    console.log("Bot message with audio:", botMessage); // Debug log
                } else if (currentOption === "6") {
                    botMessage = {
                        type: 'bot',
                        content: { text: data.response },
                        option: currentOption
                    };
                } else if (currentOption === "2") {
                    if (selectedMode === "1.1" && role === "pro") {
                        botMessage = {
                            type: 'bot',
                            content: { image_url: data.images[0].url },
                            option: currentOption
                        };
                    } else {
                        botMessage = {
                            type: 'bot',
                            content: { image_url: `http://127.0.0.1:8000/${data.image_url}` },
                            option: currentOption
                        };
                    }
                } else if (currentOption === "7") {
                    botMessage = {
                        type: 'bot',
                        content: { text: data.answer },
                        option: currentOption
                    };
                } else if (currentOption === "8") {
                    botMessage = {
                        type: 'bot',
                        content: {
                            text: typeof data.code === 'object' ? JSON.stringify(data.code) : data.code
                        },
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

            console.log("Bot message after processing:", botMessage); // Debug log

            setChatHistory(prev => [...prev, botMessage]);

            // Chuẩn bị và lưu chat detail
            const normalizedContent = normalizeBotMessageContent(botMessage);
            const payload = prepareChatDetailPayload(finalText, fileName, normalizedContent, currentOption);

            // Đảm bảo có conversation ID trước khi lưu
            if (!currentConversationId) {
                await handleNewChat();
            }

            // Lưu chat detail
            await addChatDetail(payload);

            if (!isManualSelection) setSelectedOption("0");

            // Reset về Auto Analyze sau khi xử lý xong
            setSelectedOption("0");

            // Reset file và preview
            setSelectedFile(null);
            setImagePreview(null);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
            if (imageInputRef.current) {
                imageInputRef.current.value = '';
            }

        } catch (error) {
            console.error("Lỗi:", error);
            toast.error("Có lỗi xảy ra khi gọi API: " + error.message, {
                closeButton: true,
                className: 'p-0 w-[400px] border border-red-600/40',
                ariaLabel: 'Error',
            });
            // Reset về Auto Analyze khi có lỗi
            setSelectedOption("0");
        } finally {
            setIsLoading(false);
        }
    };

    const handleSpeechFile = async (file) => {
        if (role === "free") {
            alert("Tài khoản miễn phí không được phép upload. Vui lòng nâng cấp lên Plus hoặc Pro để sử dụng tính năng này!");
            navigate('/advanced');
            return;
        }
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
            toast.error("Có lỗi xảy ra khi gọi API: " + error.message, {
                closeButton: true,
                className: 'p-0 w-[400px] border border-red-600/40',
                ariaLabel: 'Error',
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleVideoFile = async (file) => {
        if (role === "free") {
            alert("Tài khoản miễn phí không được phép upload. Vui lòng nâng cấp lên Plus hoặc Pro để sử dụng tính năng này!");
            navigate('/advanced');
            return;
        }
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
            toast.error("Gửi video thất bại: " + error.message, {
                closeButton: true,
                className: 'p-0 w-[400px] border border-red-600/40',
                ariaLabel: 'Error',
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleDocFile = async (file) => {
        if (role === "free") {
            alert("Tài khoản miễn phí không được phép upload. Vui lòng nâng cấp lên Plus hoặc Pro để sử dụng tính năng này!");
            navigate('/advanced');
            return;
        }
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
            toast.error("Có lỗi xảy ra khi gọi API: " + error.message, {
                closeButton: true,
                className: 'p-0 w-[400px] border border-red-600/40',
                ariaLabel: 'Error',
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleImproveImage = async (file) => {
        if (role === "free") {
            alert("Tài khoản miễn phí không được phép upload. Vui lòng nâng cấp lên Plus hoặc Pro để sử dụng tính năng này!");
            navigate('/advanced');
            return;
        }
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
            toast.error("Có lỗi xảy ra khi gọi API: " + error.message, {
                closeButton: true,
                className: 'p-0 w-[400px] border border-red-600/40',
                ariaLabel: 'Error',
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleManualModeToggle = () => {
        setIsManualMode(!isManualMode);
        setShowFunctionDropdown(!isManualMode);
        if (!isManualMode) {
            setSelectedOption("0"); // Reset về Auto Analyze khi tắt manual mode
        }
    };

    return (
        <div className="full-container">
            <ToastContainer
                position="top-right"
                autoClose={3000}
                hideProgressBar={true}
                closeOnClick
                pauseOnHover
                draggable
                theme="dark"
                transition={Slide}
                stacked
                icon={({ type, theme }) => {
                    // theme is not used in this example but you could
                    switch (type) {
                        case 'info':
                            return <Info className="stroke-indigo-400" />;
                        case 'error':
                            return <CircleAlert className="stroke-red-500" />;
                        case 'success':
                            return <BadgeCheck className="stroke-green-500" />;
                        case 'warning':
                            return <TriangleAlert className="stroke-yellow-500" />;
                        default:
                            return null;
                    }
                }}
            />
            <div className="sidebar">
                <button className="back-button" onClick={() => navigate('/')}>
                    <i className="fa fa-home"></i>
                </button>
                <div className="sidebar_title">
                    <h2>Sidebar</h2>
                </div>

                <div className="mode-selection">
                    <select
                        className={`options ${isLoading ? 'disabled' : ''} focus:border-blue-600`}
                        value={selectedMode}
                        onChange={handleModeChange}
                        disabled={isLoading}
                    >
                        <option value="1">API-Model 1</option>
                        <option value="1.1" disabled={role !== "pro"}>API-Model 1.1</option>
                    </select>
                </div>

                <div className="manual-mode-toggle" style={{ margin: '10px 0' }}>
                    <button
                        className={`toggle-button ${isManualMode ? 'active' : ''}`}
                        onClick={handleManualModeToggle}
                        style={{
                            padding: '8px 15px',
                            borderRadius: '5px',
                            border: 'none',
                            background: isManualMode ? 'linear-gradient(135deg, #3999ff, #50e2ff)' : '#2a2a2a',
                            color: 'white',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        }}
                    >
                        <i className={`fa ${isManualMode ? 'fa-check-circle' : 'fa-cog'}`}></i>
                        {isManualMode ? 'Chế độ thủ công' : 'Chế độ tự động'}
                    </button>
                </div>

                {showFunctionDropdown && (
                    <div className="choices">
                        <select
                            className={`options ${isLoading ? 'disabled' : ''} focus:border-blue-600`}
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
                )}

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
                    <ul className="chat-list" style={{ listStyle: 'none', padding: 0, cursor: 'pointer' }}>
                        {conversations.map((conversation) => (
                            <li
                                key={conversation.id}
                                className={`chat-item ${currentConversationId === conversation.id ? 'active' : ''}`}
                                onClick={() => loadConversation(conversation.id)}
                                style={{
                                    padding: '10px 15px',
                                    margin: '5px 0',
                                    borderRadius: '8px',
                                    backgroundColor: currentConversationId === conversation.id ? '#2a2a2a' : 'transparent',
                                    border: currentConversationId === conversation.id ? '1px solid #3999ff' : '1px solid transparent',
                                    transition: 'all 0.3s ease',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'space-between',
                                    '&:hover': {
                                        backgroundColor: '#2a2a2a',
                                        transform: 'translateX(5px)'
                                    }
                                }}
                            >
                                <span style={{
                                    color: currentConversationId === conversation.id ? '#3999ff' : '#fff',
                                    fontWeight: currentConversationId === conversation.id ? 'bold' : 'normal',
                                    transition: 'all 0.3s ease'
                                }}>
                                    {conversation.title}
                                </span>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleDeleteConversation(conversation.id);
                                    }}
                                    style={{
                                        background: 'transparent',
                                        color: '#ff4444',
                                        border: 'none',
                                        padding: '2px 6px',
                                        borderRadius: '5px',
                                        cursor: 'pointer',
                                        marginLeft: '10px',
                                        opacity: currentConversationId === conversation.id ? 1 : 0.5,
                                        transition: 'all 0.3s ease',
                                        '&:hover': {
                                            opacity: 1,
                                            backgroundColor: 'rgba(255, 68, 68, 0.1)'
                                        }
                                    }}
                                >
                                    🞬
                                </button>
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

                <div className="conversation content-item">
                    {chatHistory.map((message, index) => (
                        <div
                            key={index}
                            className={`message ${message.type}-message${message.video_url ? " video-message" : ""}${message.audio_url ? " audio-message" : ""}${message.image_url ? " image-message" : ""}`}
                        >
                            {message.type === 'user' ? (
                                message.audio_url ? (
                                    <audio controls
                                        src={message.audio_url}
                                        style={{
                                            width: "100%",
                                            maxWidth: "500px",
                                            maxHeight: "300px",
                                            borderRadius: "10px"
                                        }} />
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
                                        <audio
                                            controls
                                            src={message.content.audio_url}
                                            style={{
                                                minwidth: "100%",
                                                maxWidth: "800px",
                                                borderRadius: "10px",
                                                marginBottom: "10px"
                                            }}
                                        />
                                        <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                                            <EmailShareButton
                                                subject='My content was created by Nhom1, check it out!'
                                                body='My content was created by Nhom 1! Check it out!'
                                                className='share'
                                                style={{ color: 'white' }}
                                            >
                                                <EmailIcon size={48} round={true} />
                                            </EmailShareButton>

                                            <FacebookShareButton hashtag='#AI'>
                                                <FacebookIcon size={48} round={true} />
                                            </FacebookShareButton>
                                        </div>
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
                                            style={{ color: 'white' }}
                                        >
                                            <EmailIcon size={48} round={true} />
                                        </EmailShareButton>

                                        <FacebookShareButton hashtag='#AI'>
                                            <FacebookIcon size={48} round={true} />
                                        </FacebookShareButton>
                                    </>
                                ) : message.option === "3" ? (
                                    <>
                                        <video controls width="100%" src={message.content.video_url} />
                                        <EmailShareButton subject='My content was created by Nhom1, check it out!'
                                            body='My content was created by Nhom 1! Check it out!' className='share' style={{ color: 'white', borderRadius: '10px' }}>
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
                                            style={{ color: 'white' }}
                                        >
                                            <EmailIcon size={48} round={true} />
                                        </EmailShareButton>
                                        <FacebookShareButton hashtag='#AI'>
                                            <FacebookIcon size={48} round={true} />
                                        </FacebookShareButton>
                                    </>
                                ) : (message.option === "6" || message.option === "7" || message.option === "8" || message.option === "9" || message.option === "10" || message.option === "11" || message.option === "12") ? (
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
                    <div id="btn_complex" style={{ position: 'relative', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                        {selectedOption === "0" ? (
                            <>


                                <textarea
                                    className={`input ${isLoading ? 'disabled' : ''}  focus:border-blue-600`}
                                    id="textarea"
                                    rows="4"
                                    placeholder="Mô tả những gì bạn muốn tạo, hoặc chọn file để phân tích (Video: .mp4/ Audio: .wav, .mp3/ File: .pdf, .doc, .docx, .txt)"
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter' && !e.shiftKey) {
                                            e.preventDefault();
                                            handleSubmit(inputValue);
                                            setInputValue('');
                                        }
                                    }}
                                    disabled={isLoading}
                                />
                                <button
                                    className={`file-upload-btn ${isLoading ? 'disabled' : ''}`}
                                    onClick={() => fileInputRef.current?.click()}
                                    disabled={isLoading}
                                    data-tooltip="Nhập liệu bằng video
                                        âm thanh, hình ảnh"
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
                                <button
                                    className={`file-upload-btn ${isLoading ? 'disabled' : ''}`}
                                    onClick={() => imageInputRef.current?.click()}
                                    disabled={isLoading}
                                    data-tooltip="Đính kèm tệp"
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
                                        background: 'none',
                                        border: 'none',
                                        color: 'black',
                                        fontSize: '25px',
                                        position: 'absolute',
                                        left: '50px'
                                    }}
                                >
                                    📎
                                </button>
                                <input
                                    type="file"
                                    ref={imageInputRef}
                                    onChange={handleImageSelect}
                                    style={{ display: 'none' }}
                                    accept="image/*"
                                />
                                {imagePreview && (
                                    <div style={{
                                        position: 'absolute',
                                        top: '-40px',
                                        left: '4%',
                                        transform: 'translateX(-50%)',
                                        width: '50px',
                                        height: '50px',
                                        borderRadius: '5px',
                                        overflow: 'hidden',
                                        border: 'none'
                                    }}>
                                        <img
                                            src={imagePreview}
                                            alt="Preview"
                                            style={{
                                                width: '100%',
                                                height: '100%',
                                                objectFit: 'cover'
                                            }}
                                        />
                                        <button
                                            onClick={() => {
                                                setSelectedFile(null);
                                                setImagePreview(null);
                                                if (imageInputRef.current) {
                                                    imageInputRef.current.value = '';
                                                }
                                            }}
                                            style={{
                                                position: 'absolute',
                                                top: '2px',
                                                right: '2px',
                                                width: '16px',
                                                height: '16px',
                                                borderRadius: '50%',
                                                background: '#ff4444',
                                                border: 'none',
                                                color: 'white',
                                                fontSize: '10px',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                cursor: 'pointer',
                                                padding: 0,
                                                lineHeight: 1,
                                                boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                                                zIndex: 2,
                                                transition: 'transform 0.2s ease',
                                                ':hover': {
                                                    transform: 'scale(1.2)'
                                                }
                                            }}
                                        >
                                            ×
                                        </button>
                                    </div>
                                )}
                                <div className="glow-wrapper">
                                    <button
                                        id="submit_btn"
                                        className={isLoading ? 'disabled' : ''}
                                        onClick={() => {
                                            handleSubmit(inputValue);
                                            setInputValue('');
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
                                {localStorage.getItem("role") !== "free" ? (
                                    <>
                                        <FileUpload onFileSend={handleSpeechFile} accept=".wav" disabled={isLoading} />
                                        <span style={{ color: "#fff" }}>
                                            Hãy chọn file (.wav,.mp3) để chuyển thành văn bản...
                                        </span>
                                    </>
                                ) : (
                                    <div style={{
                                        display: 'flex',
                                        flexDirection: 'column',
                                        alignItems: 'center',
                                        gap: '10px'
                                    }}>
                                        <span style={{ color: "#fff", textAlign: 'center' }}>
                                            Tài khoản miễn phí không được phép upload. Vui lòng nâng cấp lên Plus hoặc Pro để sử dụng tính năng này!
                                        </span>
                                        <div className="fixed-button-container-2">
                                            <button
                                                className="rainbow-button"
                                                onClick={() => navigate('/advanced')}
                                                style={{
                                                    padding: '10px 20px',
                                                    borderRadius: '5px',
                                                    border: 'none',
                                                    cursor: 'pointer',
                                                    fontSize: '14px'
                                                }}
                                            >
                                                Nâng cấp ngay
                                            </button>
                                        </div>
                                    </div>
                                )}
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
                                {role !== "free" ? (
                                    <>
                                        <FileUpload onFileSend={handleVideoFile} accept=".mp4" disabled={isLoading} />
                                        <span style={{ color: "#fff" }}>
                                            Hãy chọn file video (.mp4) để chuyển thành văn bản...
                                        </span>
                                    </>
                                ) : (
                                    <div style={{
                                        display: 'flex',
                                        flexDirection: 'column',
                                        alignItems: 'center',
                                        gap: '10px'
                                    }}>
                                        <span style={{ color: "#fff", textAlign: 'center' }}>
                                            Tài khoản miễn phí không được phép upload. Vui lòng nâng cấp lên Plus hoặc Pro để sử dụng tính năng này!
                                        </span>
                                        <div className="fixed-button-container-2">
                                            <button
                                                className="rainbow-button"
                                                onClick={() => navigate('/advanced')}
                                                style={{
                                                    padding: '10px 20px',
                                                    borderRadius: '5px',
                                                    border: 'none',
                                                    cursor: 'pointer',
                                                    fontSize: '14px'
                                                }}
                                            >
                                                Nâng cấp ngay
                                            </button>
                                        </div>
                                    </div>
                                )}
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
                                {role !== "free" ? (
                                    <>
                                        <FileUpload onFileSend={handleDocFile} accept=".docx,.txt" disabled={isLoading} />
                                        <span style={{ color: "#fff" }}>
                                            Hãy chọn file (.pdf, .doc, .docx, .txt) để chuyển thành văn bản...
                                        </span>
                                    </>
                                ) : (
                                    <div style={{
                                        display: 'flex',
                                        flexDirection: 'column',
                                        alignItems: 'center',
                                        gap: '10px'
                                    }}>
                                        <span style={{ color: "#fff", textAlign: 'center' }}>
                                            Tài khoản miễn phí không được phép upload. Vui lòng nâng cấp lên Plus hoặc Pro để sử dụng tính năng này!
                                        </span>
                                        <div className="fixed-button-container-2">
                                            <button
                                                className="rainbow-button"
                                                onClick={() => navigate('/advanced')}
                                                style={{
                                                    padding: '10px 20px',
                                                    borderRadius: '5px',
                                                    border: 'none',
                                                    cursor: 'pointer',
                                                    fontSize: '14px'
                                                }}
                                            >
                                                Nâng cấp ngay
                                            </button>
                                        </div>
                                    </div>
                                )}
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
                                {role !== "free" ? (
                                    <>
                                        <FileUpload onFileSend={handleImproveImage} accept=".jpg" disabled={isLoading} />
                                        <span style={{ color: "#fff" }}>
                                            Hãy chọn file ảnh (.jpg) để cải thiện chất lượng...
                                        </span>
                                    </>
                                ) : (
                                    <div style={{
                                        display: 'flex',
                                        flexDirection: 'column',
                                        alignItems: 'center',
                                        gap: '10px'
                                    }}>
                                        <span style={{ color: "#fff", textAlign: 'center' }}>
                                            Tài khoản miễn phí không được phép upload. Vui lòng nâng cấp lên Plus hoặc Pro để sử dụng tính năng này!
                                        </span>
                                        <div className="fixed-button-container-2">
                                            <button
                                                className="rainbow-button"
                                                onClick={() => navigate('/advanced')}
                                                style={{
                                                    padding: '10px 20px',
                                                    borderRadius: '5px',
                                                    border: 'none',
                                                    cursor: 'pointer',
                                                    fontSize: '14px'
                                                }}
                                            >
                                                Nâng cấp ngay
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <>
                                <textarea
                                    className={`input ${isLoading ? 'disabled' : ''}  focus:border-blue-600`}
                                    rows="4"
                                    placeholder="Mô tả những gì bạn muốn tạo"
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter' && !e.shiftKey) {
                                            e.preventDefault();
                                            handleSubmit(inputValue);
                                            setInputValue('');
                                        }
                                    }}
                                    disabled={isLoading}
                                />
                                <div className="glow-wrapper">
                                    <button
                                        id="submit_btn"
                                        className={isLoading ? 'disabled' : ''}
                                        onClick={() => {
                                            handleSubmit(inputValue);
                                            setInputValue('');
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