import React, { createContext, useState, useEffect, useCallback } from "react";
import { toast } from "react-toastify";
import Cookies from "js-cookie";
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

	useEffect(() => {
		const init = async () => {
			try {
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

				const chatHistories = await ApiService.fetchChatHistories();
				setConversations(chatHistories);
			} catch (error) {
				toast.error(error.message);
			}
		};
		init();
	}, []);

	const handleAutoAnalyze = useCallback(
		async (text) => {
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
				const actionMap = {
					generate_text: "6",
					generate_image: "2",
					generate_video: "3",
					generate_code: "8",
					generate_speech: "1",
					generate_answer: "7",
				};
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

	const sendMessage = useCallback(
		async (text, file, option) => {
			if (isRateLimited) {
				toast.error("Hết lượt miễn phí. Vui lòng thử lại sau.");
				return;
			}
			setIsLoading(true);
			try {
				let finalOption = option;
				let finalText = text;
				if (option === "0" && text) {
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
				}

				if (text && !file) {
					setMessages((prev) => [
						...prev,
						{
							id: Date.now(),
							type: "user",
							content: text,
							isText: true,
						},
					]);
					const response = await ApiService.processText(
						finalText,
						finalOption,
						role
					);
					const botMessage = await ApiService.normalizeBotMessage(
						response,
						finalOption
					);
					setMessages((prev) => [
						...prev,
						{ id: Date.now(), ...botMessage },
					]);
				} else if (file) {
					if (role === "free") {
						toast.error(
							"Tài khoản miễn phí không được phép upload!"
						);
						return;
					}
					const userMessage = await ApiService.createUserFileMessage(
						file,
						finalOption
					);
					setMessages((prev) => [
						...prev,
						{ id: Date.now(), ...userMessage },
					]);
					const response = await ApiService.processFile(
						file,
						finalOption
					);
					const botMessage = await ApiService.normalizeBotMessage(
						response,
						finalOption
					);
					setMessages((prev) => [
						...prev,
						{ id: Date.now(), ...botMessage },
					]);
				}

				if (!currentConversationId) {
					await createConversation();
				}
				// TODO: Lưu chi tiết tin nhắn vào API
			} catch (error) {
				toast.error("Lỗi: " + error.message);
			} finally {
				setIsLoading(false);
			}
		},
		[isRateLimited, role, currentConversationId, handleAutoAnalyze]
	);

	const loadConversation = useCallback(async (id) => {
		try {
			setIsLoading(true);
			const conversation = await ApiService.getConversation(id);
			setMessages(conversation.messages || []);
			setCurrentConversationId(id);
		} catch (error) {
			toast.error("Lỗi khi tải cuộc trò chuyện: " + error.message);
		} finally {
			setIsLoading(false);
		}
	}, []);

	const createConversation = useCallback(async () => {
		try {
			setIsLoading(true);
			const newConversation = await ApiService.createConversation(email);
			setConversations((prev) => [...prev, newConversation]);
			setCurrentConversationId(newConversation.id);
			setMessages([]);
		} catch (error) {
			toast.error("Lỗi khi tạo cuộc trò chuyện: " + error.message);
		} finally {
			setIsLoading(false);
		}
	}, [email]);

	const deleteConversation = useCallback(
		async (id) => {
			try {
				setIsLoading(true);
				await ApiService.deleteConversation(id);
				setConversations((prev) =>
					prev.filter((conv) => conv.id !== id)
				);
				if (currentConversationId === id) {
					setCurrentConversationId(null);
					setMessages([]);
				}
			} catch (error) {
				toast.error("Lỗi khi xóa cuộc trò chuyện: " + error.message);
			} finally {
				setIsLoading(false);
			}
		},
		[currentConversationId]
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
				deleteConversation,
			}}
		>
			{children}
		</ChatContext.Provider>
	);
};
