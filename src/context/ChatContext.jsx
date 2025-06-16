import React, { createContext, useState, useEffect, useCallback } from "react";
import { toast } from "react-toastify";
import ApiService from "@/utils/api_services";

export const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
	const [role, setRole] = useState(localStorage.getItem("role") || "free");
	const [email, setEmail] = useState(localStorage.getItem("email") || "");
	const [selectedOption, setSelectedOption] = useState("0");
	const [messages, setMessages] = useState([]);
	const [conversations, setConversations] = useState([]);
	const [currentConversationId, setCurrentConversationId] = useState(null);
	const [isLoading, setIsLoading] = useState(false);
	const [isRateLimited, setIsRateLimited] = useState(false);
	const [retryAfter, setRetryAfter] = useState(0);
	const generatorIdMap = {
		0: "00000000-0000-0000-0000-000000000000", // Auto analyze
		1: "01010101-0101-0101-0101-010101010101", // Text to speech (default)
		2: "22222222-2222-2222-2222-222222222222", // Text to image
		3: "33333333-3333-3333-3333-333333333333", // Text to video
		4: "44444444-4444-4444-4444-444444444444", // Text to speech (custom)
		5: "55555555-5555-5555-5555-555555555555", // Enhance image
		6: "66666666-6666-6666-6666-666666666666", // AI - chatbot
		7: "77777777-7777-7777-7777-777777777777", // Answer question
		8: "88888888-8888-8888-8888-888888888888", // Generate code
		9: "99999999-9999-9999-9999-999999999999", // Speech to text
		10: "10101010-1010-1010-1010-101010101010", // Video to text
		11: "11111111-1111-1111-1111-111111111111", // File to text
	};
	const actionMap = {
		generate_text: "6",
		generate_image: "2",
		generate_video: "3",
		generate_code: "8",
		generate_speech: "1",
		generate_answer: "7",
	};

	// Load lịch sử chat khi component mount
	useEffect(() => {
		const initializeChat = async () => {
			try {
				setIsLoading(true);
				const histories = await ApiService.fetchChatHistories();
				const reversedHistories = histories.reverse();
				setConversations(reversedHistories);

				if (reversedHistories.length > 0) {
					const latestConversation = reversedHistories[0];
					setCurrentConversationId(latestConversation.id);
					await loadConversation(latestConversation.id);
				} else {
					const newConversation = await createConversation();
					setCurrentConversationId(newConversation.id);
				}
			} catch (error) {
				toast.error("Lỗi khi khởi tạo chat: " + error.message);
				const newConversation = await createConversation();
				setCurrentConversationId(newConversation.id);
			} finally {
				setIsLoading(false);
			}
		};
		initializeChat();
	}, []);

	// Load thông tin cần thiết cho user
	useEffect(() => {
		const init = async () => {
			try {
				setIsLoading(true);
				const userInfo = await ApiService.getUserInfo();
				if (!userInfo.email) {
					throw new Error("Không tìm thấy email!");
				}
				setEmail(userInfo.email);
				localStorage.setItem("email", userInfo.email);

				const subscription = await ApiService.getUserSubscription(
					userInfo.email
				);
				setRole(subscription.role);
				localStorage.setItem("role", subscription.role);
				localStorage.setItem(
					"billingCycle",
					subscription.billingCycle || "monthly"
				);
			} catch (error) {
				toast.error("Lỗi khi khởi tạo chat: " + error.message);
			} finally {
				setIsLoading(false);
			}
		};
		init();
	}, []);

	// Xóa bộ đếm giờ
	useEffect(() => {
		return () => {
			const timers = document.querySelectorAll("body").__timers || [];
			timers.forEach(clearInterval);
		};
	}, []);

	const handleAutoAnalyze = useCallback(
		async (text) => {
			if (!text.trim()) {
				toast.error("Vui lòng nhập nội dung để phân tích.");
				return { success: false, error: "Empty input" };
			}
			if (isRateLimited)
				return { success: false, error: "Rate limit exceeded" };
			try {
				setIsLoading(true);
				const response = await ApiService.analyzeText(
					text,
					email,
					role
				);
				if (response.status === 429) {
					const timeToWait =
						parseInt(response.headers.get("Retry-After"), 10) *
							1000 || 5000;
					setRetryAfter(timeToWait);
					setIsRateLimited(true);
					toast.error("Hết lượt miễn phí. Vui lòng thử lại sau.");
					const timer = setInterval(() => {
						setRetryAfter((prev) => {
							if (prev <= 1) {
								clearInterval(timer);
								setIsRateLimited(false);
								return 0;
							}
							return prev - 1;
						});
					}, 1000);
					return { success: false, error: "Rate limit exceeded" };
				}
				const data = await response.json();

				if (data.intent_analysis && actionMap[data.intent_analysis]) {
					const action = actionMap[data.intent_analysis];
					if (action === "3" && role !== "pro") {
						toast.error(
							"Chỉ tài khoản Pro mới được phép sử dụng Text to Video!"
						);
						return { success: false, error: "Restricted access" };
					}
					return {
						success: true,
						intent_analysis: data.intent_analysis,
						prompt: text,
						action,
					};
				}
				toast.error(
					"Không thể phân tích yêu cầu. Vui lòng chọn chức năng thủ công."
				);
				return { success: false, error: "Không thể phân tích yêu cầu" };
			} catch (error) {
				toast.error("Lỗi khi phân tích: " + error.message);
				return { success: false, error: error.message };
			} finally {
				setIsLoading(false);
			}
		},
		[email, role, isRateLimited]
	);

	const loadConversation = useCallback(async (id) => {
		try {
			setIsLoading(true);
			const conversation = await ApiService.getConversation(
				id,
				generatorIdMap
			);
			setMessages(conversation.messages || []);
			setCurrentConversationId(id);
		} catch (error) {
			toast.error("Lỗi khi tải cuộc trò chuyện: " + error.message);
		} finally {
			setIsLoading(false);
		}
	}, []);

	const createConversation = useCallback(
		async (initialMessages = []) => {
			try {
				setIsLoading(true);
				const newConversation = await ApiService.createConversation(
					initialMessages
				);
				setConversations((prev) => [newConversation, ...prev]);
				setCurrentConversationId(newConversation.id);
				setMessages([]);
				return newConversation;
			} catch (error) {
				toast.error("Lỗi khi tạo cuộc trò chuyện: " + error.message);
				throw error;
			} finally {
				setIsLoading(false);
			}
		},
		[setConversations, setMessages]
	);

	const deleteChatHistory = useCallback(
		async (id) => {
			try {
				setIsLoading(true);
				await ApiService.deleteChatHistory(id);
				setConversations((prev) =>
					prev.filter((conv) => conv.id !== id)
				);
				if (currentConversationId === id) {
					setCurrentConversationId(null);
					setMessages([]);
					if (conversations.length === 1) {
						const newConversation = await createConversation();
						setCurrentConversationId(newConversation.id);
					} else if (conversations.length > 1) {
						const latest = conversations.filter(
							(conv) => conv.id !== id
						)[0];
						setCurrentConversationId(latest.id);
						await loadConversation(latest.id);
					}
				}
			} catch (error) {
				toast.error("Lỗi khi xóa cuộc trò chuyện: " + error.message);
			} finally {
				setIsLoading(false);
			}
		},
		[
			currentConversationId,
			setConversations,
			setMessages,
			conversations,
			loadConversation,
		]
	);

	const sendMessage = useCallback(
		async (text, file, option) => {
			if (file && role === "free") {
				toast.error("Tài khoản miễn phí không được phép upload file.", {
					closeButton: true,
					className:
						"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
				});
				return;
			}
			if (isRateLimited) {
				toast.error("Hết lượt miễn phí. Vui lòng thử lại sau.");
				return;
			}
			setIsLoading(true);
			try {
				let finalOption = option;
				let finalText = text || "";
				let userMessage;

				// Xử lý mode 0 (Auto Analyze)
				if (option === "0") {
					if (text && file) {
						const analyzeResult =
							await ApiService.analyzeTextAndFile(
								finalText,
								file,
								email,
								role
							);
						if (!analyzeResult.ok)
							throw new Error("Phân tích text và file thất bại");
						const data = await analyzeResult.json();
						if (data.intent_analysis) {
							finalOption =
								actionMap[data.intent_analysis] || finalOption;
							setMessages((prev) => [
								...prev,
								{
									id: Date.now(),
									type: "bot",
									content:
										"[AutoAnalyze đã xác định chức năng phù hợp]",
									isText: true,
								},
							]);
						}
					} else if (text) {
						const analyzeResult = await handleAutoAnalyze(text);
						if (!analyzeResult.success) return;
						finalOption = analyzeResult.action;
						finalText = analyzeResult.prompt;
						setMessages((prev) => [
							...prev,
							{
								id: Date.now(),
								type: "bot",
								content:
									"[AutoAnalyze đã xác định chức năng phù hợp]",
								isText: true,
							},
						]);
					} else if (file) {
						const analyzeResult = await ApiService.analyzeFile(
							file,
							email,
							role
						);
						if (!analyzeResult.ok)
							throw new Error("Phân tích file thất bại");
						const data = await analyzeResult.json();
						if (data.intent_analysis) {
							finalOption =
								actionMap[data.intent_analysis] || finalOption;
							setMessages((prev) => [
								...prev,
								{
									id: Date.now(),
									type: "bot",
									content:
										"[AutoAnalyze đã xác định chức năng phù hợp]",
									isText: true,
								},
							]);
						}
					}
				}

				// Validation
				const textOnlyOptions = ["1", "2", "3", "6", "7", "8"];
				const fileOnlyOptions = ["5", "9", "10", "11"];
				const textAndFileOptions = ["0", "4"];

				if (
					textOnlyOptions.includes(finalOption) &&
					!finalText.trim()
				) {
					toast.error("Vui lòng nhập nội dung.");
					return;
				}
				if (fileOnlyOptions.includes(finalOption) && !file) {
					toast.error("Vui lòng chọn file.");
					return;
				}
				if (
					textAndFileOptions.includes(finalOption) &&
					!finalText.trim() &&
					!file
				) {
					toast.error("Vui lòng nhập nội dung hoặc chọn file.");
					return;
				}
				if (
					finalOption === "4" &&
					(!finalText.trim() ||
						!file ||
						!file.name.toLowerCase().endsWith(".wav"))
				) {
					toast.error("Mode 4 yêu cầu cả text và file .wav!");
					return;
				}

				// Tạo user message
				if (finalText && file) {
					userMessage = await ApiService.createUserMessage(
						finalText,
						file,
						finalOption
					);
				} else if (finalText) {
					userMessage = await ApiService.createUserMessage(
						finalText,
						null,
						finalOption
					);
				} else if (file) {
					userMessage = await ApiService.createUserMessage(
						"",
						file,
						finalOption
					);
				}
				userMessage.id = Date.now();
				setMessages((prev) => [...prev, userMessage]);

				// Gọi API
				let response;
				if (finalText && file) {
					response = await ApiService.processTextAndFile(
						finalText,
						file,
						finalOption,
						role
					);
				} else if (finalText) {
					response = await ApiService.processText(
						finalText,
						finalOption,
						role
					);
				} else if (file) {
					response = await ApiService.processFile(file, finalOption);
				}

				if (!response.ok)
					throw new Error(`API error: ${await response.text()}`);

				const botMessage = await ApiService.normalizeBotMessage(
					response,
					finalOption
				);
				botMessage.id = Date.now();
				setMessages((prev) => [...prev, botMessage]);

				// Tạo hoặc cập nhật conversation
				if (!currentConversationId) {
					const newConversation = await createConversation();
					setCurrentConversationId(newConversation.id);
				}

				console.log(
					`chatcontext: bot content ${botMessage.output_file_path}`
				);
				// Gọi addChatDetail với generatorIdMap
				await ApiService.addChatDetail(
					{
						input_type: userMessage.input_type || "text",
						input_text:
							typeof userMessage.content === "string"
								? userMessage.content
								: userMessage.content.text || "",
						input_file_name: userMessage.file_name,
						input_file_path:
							userMessage.audio_url ||
							userMessage.image_url ||
							userMessage.video_url ||
							userMessage.file_url,
						output_type: botMessage.isText
							? "text"
							: botMessage.isAudio
							? "audio"
							: botMessage.isImage
							? "image"
							: botMessage.isVideo
							? "video"
							: "file",
						output_text: botMessage.content.text || null,
						output_file_name: null,
						output_file_path: botMessage.output_file_path || null,
						generator_id: finalOption,
					},
					currentConversationId,
					generatorIdMap
				);
			} catch (error) {
				toast.error("Lỗi: " + error.message);
				console.error("Error in sendMessage:", error);
			} finally {
				setIsLoading(false);
			}
		},
		[
			isRateLimited,
			role,
			currentConversationId,
			handleAutoAnalyze,
			email,
			createConversation,
		]
	);

	return (
		<ChatContext.Provider
			value={{
				role,
				email,
				selectedOption,
				setSelectedOption,
				messages,
				conversations,
				currentConversationId,
				isLoading,
				isRateLimited,
				retryAfter,
				sendMessage,
				handleAutoAnalyze,
				loadConversation,
				createConversation,
				deleteChatHistory,
			}}
		>
			{children}
		</ChatContext.Provider>
	);
};
