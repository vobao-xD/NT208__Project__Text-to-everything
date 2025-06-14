import Cookies from "js-cookie";

const ApiService = {
	// Hàm tiện ích: Xác định loại file đầu vào
	detectInputFileType(filename) {
		const ext = filename.split(".").pop().toLowerCase();
		if (["mp3", "wav"].includes(ext)) return "audio";
		if (["png", "jpg", "jpeg"].includes(ext)) return "image";
		if (["mp4", "avi", "mov"].includes(ext)) return "video";
		if (["pdf", "txt", "doc", "docx"].includes(ext)) return "file";
		return "file";
	},

	// Hàm tiện ích: Ánh xạ tùy chọn sang loại dữ liệu
	mapOptionToType(option) {
		switch (option) {
			case "1":
				return "audio";
			case "2":
				return "image";
			case "3":
				return "video";
			case "4":
				return "file";
			default:
				return "text";
		}
	},

	// Hàm tiện ích: Chuẩn bị payload cho chi tiết chat
	prepareChatDetailPayload(
		inputText,
		inputFileName,
		inputFile,
		normalizedContent,
		generatorId,
		selectedOption
	) {
		return {
			input_type: inputFileName
				? this.detectInputFileType(inputFileName)
				: this.mapOptionToType(selectedOption),
			input_text: inputFileName ? null : inputText,
			input_file_name: inputFileName || null,
			input_file: inputFile || null,
			output_type: normalizedContent.type,
			output_text: normalizedContent.text || null,
			output_image_url: normalizedContent.image_url || null,
			output_audio_url: normalizedContent.audio_url || null,
			output_video_url: normalizedContent.video_url || null,
			output_file_url: normalizedContent.file_url || null,
			output_file_name: normalizedContent.file_name || null,
			generator_id: generatorId,
		};
	},

	// Lấy thông tin người dùng
	async getUserInfo() {
		const response = await fetch(
			"http://localhost:8000/auth/get-user-info",
			{
				method: "GET",
				credentials: "include",
			}
		);
		if (!response.ok)
			throw new Error(
				`Lỗi khi lấy thông tin người dùng: ${await response.text()}`
			);
		return await response.json();
	},

	// Lấy vai trò người dùng
	async getUserSubscription(email) {
		const response = await fetch(
			`http://localhost:8000/user-subscription?email=${email}`,
			{
				method: "GET",
				credentials: "include",
			}
		);
		if (!response.ok)
			throw new Error(
				`Lỗi khi lấy thông tin vai trò: ${await response.text()}`
			);
		return await response.json();
	},

	// Phân tích văn bản
	async analyzeText(text, email, role) {
		const response = await fetch("http://localhost:8000/analyze", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			credentials: "include",
			body: JSON.stringify({ user_text: text }),
		});
		return response; // Trả về response để xử lý status 429 trong ChatContext
	},

	// Xử lý văn bản theo tùy chọn
	async processText(text, option, role) {
		let apiUrl, requestBody;
		const headers = {
			"Content-Type": "application/json",
		};

		switch (option) {
			case "1":
				apiUrl =
					role === "pro"
						? "http://localhost:8000/advanced/text-to-speech"
						: "http://localhost:8000/text-to-speech/default";
				requestBody = {
					text,
					language: "Tiếng Việt",
					gender: "male",
					style: "default",
				};
				break;
			case "2":
				apiUrl =
					role === "pro"
						? "http://localhost:8000/advanced/text-to-image"
						: "http://localhost:8000/text-to-image";
				requestBody = {
					prompt: text,
					n: 1,
					size: "1024x1024",
					quality: "standard",
					style: "vivid",
				};
				break;
			case "3":
				if (role !== "pro")
					throw new Error(
						"Chỉ tài khoản Pro được phép sử dụng Text to Video!"
					);
				apiUrl = "http://localhost:8000/text-to-video";
				requestBody = {
					prompt: text,
					guidance_scale: 5.0,
					fps: 16,
					steps: 30,
					frames: 64,
				};
				break;
			case "6":
				apiUrl =
					role === "pro"
						? "http://localhost:8000/advanced/chatbot-content"
						: "http://localhost:8000/chatbot/content";
				requestBody = {
					user_input: text,
					history: [],
					system_prompt: "You are a helpful chatbot.",
					max_tokens: 500,
				};
				break;
			case "7":
				apiUrl =
					role === "pro"
						? "http://localhost:8000/advanced/generate-answer"
						: "http://localhost:8000/generate_answer";
				requestBody = { question: text, max_tokens: 500 };
				break;
			case "8":
				apiUrl =
					role === "pro"
						? "http://localhost:8000/advanced/text-to-code"
						: "http://localhost:8000/text-to-code";
				requestBody = {
					prompt: text,
					language: "python",
					max_tokens: 150,
				};
				break;
			default:
				throw new Error("Tính năng không được hỗ trợ!");
		}

		const response = await fetch(apiUrl, {
			method: "POST",
			headers,
			body: JSON.stringify(requestBody),
			credentials: "include",
		});
		if (!response.ok) throw new Error(`Lỗi API: ${await response.text()}`);
		return response;
	},

	// Xử lý file
	async processFile(file, option) {
		const formData = new FormData();
		formData.append("file", file);
		let apiUrl;

		switch (option) {
			case "5":
				apiUrl = "http://localhost:8000/enhance";
				break;
			case "9":
				apiUrl = "http://localhost:8000/input/speech";
				break;
			case "10":
				apiUrl = "http://localhost:8000/input/video";
				break;
			case "11":
				apiUrl = "http://localhost:8000/input/document";
				break;
			default:
				throw new Error("Tính năng không được hỗ trợ!");
		}

		const response = await fetch(apiUrl, {
			method: "POST",
			body: formData,
			credentials: "include",
			headers: { Authorization: `Bearer ${Cookies.get("access_token")}` },
		});
		if (!response.ok) throw new Error(`Lỗi API: ${await response.text()}`);
		return response;
	},

	// Chuẩn hóa phản hồi bot
	async normalizeBotMessage(response, option) {
		let botMessage = { type: "bot" };
		if (option === "3" || option === "5") {
			const blob = await response.blob();
			botMessage.content =
				option === "3"
					? { video_url: URL.createObjectURL(blob) }
					: { image_url: URL.createObjectURL(blob) };
			botMessage[`is${option === "3" ? "Video" : "Image"}`] = true;
			botMessage.type = option === "3" ? "video" : "image";
		} else if (option === "1" || option === "2") {
			const data = await response.json();
			const fileResponse = await fetch(
				`http://localhost:8000/get-output/${data.file_path}`,
				{
					method: "GET",
					headers: {
						Authorization: `Bearer ${Cookies.get("access_token")}`,
					},
					credentials: "include",
				}
			);
			if (!fileResponse.ok)
				throw new Error(`Lỗi tải file: ${await fileResponse.text()}`);
			const blob = await fileResponse.blob();
			botMessage.content =
				option === "1"
					? { audio_url: URL.createObjectURL(blob) }
					: { image_url: URL.createObjectURL(blob) };
			botMessage[`is${option === "1" ? "Audio" : "Image"}`] = true;
			botMessage.type = option === "1" ? "audio" : "image";
		} else {
			const data = await response.json();
			botMessage.content = {
				text:
					option === "8"
						? typeof data.code === "object"
							? JSON.stringify(data.code)
							: data.code
						: data.text || data.response || data.answer,
			};
			botMessage.isText = true;
			botMessage.type = "text";
		}
		return botMessage;
	},

	// Tạo tin nhắn người dùng cho file
	async createUserFileMessage(file, option) {
		const fileExtension = file.name.split(".").pop().toLowerCase();
		const url = URL.createObjectURL(file);
		let message = {
			type: "user",
			content: `Đã gửi ${
				option === "9"
					? "file audio"
					: option === "10"
					? "video"
					: option === "11"
					? "file"
					: "ảnh"
			}: ${file.name}`,
		};
		if (option === "5") {
			message.isImage = true;
			message.image_url = url;
			message.input_type = "image";
		} else if (option === "9") {
			message.isAudio = true;
			message.audio_url = url;
			message.input_type = "audio";
		} else if (option === "10") {
			message.isVideo = true;
			message.video_url = url;
			message.input_type = "video";
		} else if (option === "11") {
			message.isFile = true;
			message.file_url = url;
			message.fileName = file.name;
			message.input_type = "file";
		}
		return message;
	},

	// Lấy lịch sử chat
	async fetchChatHistories() {
		const token = Cookies.get("access_token");
		if (!token) throw new Error("Không tìm thấy token xác thực");
		const response = await fetch(
			"http://localhost:8000/chat-history?limit=50",
			{
				method: "GET",
				headers: {
					"Content-Type": "application/json",
					Authorization: `Bearer ${token}`,
				},
				credentials: "include",
			}
		);
		if (!response.ok)
			throw new Error(`Lỗi tải lịch sử chat: ${await response.text()}`);
		const data = await response.json();

		return data.map((c) => {
			const details = c.details || []; // Gán mảng rỗng nếu details undefined
			const firstPrompt = details[0]?.input_text || "Cuộc trò chuyện mới";
			const title =
				firstPrompt.length > 30
					? firstPrompt.substring(0, 30) + "..."
					: firstPrompt;
			return {
				id: c.id,
				title,
				messages: details,
			};
		});
	},

	// Tạo cuộc trò chuyện mới
	async createConversation(messages = []) {
		const token = Cookies.get("access_token");
		if (!token) throw new Error("Không tìm thấy token xác thực");
		const response = await fetch("http://localhost:8000/chat-history", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${token}`,
			},
			body: JSON.stringify({ chat_details: [] }),
			credentials: "include",
		});
		if (!response.ok)
			throw new Error(
				`Lỗi tạo cuộc trò chuyện mới: ${await response.text()}`
			);
		const data = await response.json();
		const conversationId = data.id;
		let title = "Cuộc trò chuyện mới";
		if (messages.length > 0) {
			const firstPrompt = messages[0].content;
			title =
				firstPrompt.length > 30
					? firstPrompt.substring(0, 30) + "..."
					: firstPrompt;
		}
		return { id: conversationId, title, messages: [] };
	},

	// Tải cuộc trò chuyện
	async getConversation(conversationId, generatorIdMap) {
		const token = Cookies.get("access_token");
		if (!token) throw new Error("Không tìm thấy token xác thực");
		const response = await fetch(
			`http://localhost:8000/chat-history/${conversationId}`,
			{
				method: "GET",
				headers: {
					"Content-Type": "application/json",
					Authorization: `Bearer ${token}`,
				},
				credentials: "include",
			}
		);
		if (!response.ok)
			throw new Error(
				`Lỗi tải cuộc trò chuyện: ${await response.text()}`
			);
		const data = await response.json();
		const messages = [];

		for (let detail of data.details) {
			const userMsg = {
				type: "user",
				content:
					detail.input_text ||
					`[Đã gửi tệp: ${detail.input_file_name || "File"}]`,
				isText: !detail.input_file_path,
				isAudio: detail.input_type === "audio",
				isImage: detail.input_type === "image",
				isVideo: detail.input_type === "video",
				isFile: detail.input_type === "file",
				audio_url:
					detail.input_type === "audio"
						? detail.input_file_path
						: null,
				image_url:
					detail.input_type === "image"
						? detail.input_file_path
						: null,
				video_url:
					detail.input_type === "video"
						? detail.input_file_path
						: null,
				file_url:
					detail.input_type === "file"
						? detail.input_file_path
						: null,
				file_name: detail.input_file_name || null,
			};
			messages.push(userMsg);

			const botMsg = {
				type: "bot",
				content: {
					text: detail.output_text || null,
					image_url: detail.output_image_url || null,
					audio_url: detail.output_audio_url || null,
					video_url: detail.output_video_url || null,
					file_url: detail.output_file_path || null,
					file_name: detail.output_file_name || null,
				},
				isText: detail.output_type === "text",
				isAudio: detail.output_type === "audio",
				isImage: detail.output_type === "image",
				isVideo: detail.output_type === "video",
				isFile: detail.output_type === "file",
				option: Object.keys(generatorIdMap).find(
					(key) => generatorIdMap[key] === detail.generator_id
				),
			};
			messages.push(botMsg);
		}

		return {
			id: conversationId,
			title:
				data.details[0]?.input_text?.substring(0, 30) + "..." ||
				"Cuộc trò chuyện mới",
			messages,
		};
	},

	// Xóa cuộc trò chuyện
	async deleteConversation(conversationId) {
		const token = Cookies.get("access_token");
		if (!token) throw new Error("Không tìm thấy token xác thực");
		const response = await fetch(
			`http://localhost:8000/chat-history/${conversationId}`,
			{
				method: "DELETE",
				headers: {
					"Content-Type": "application/json",
					Authorization: `Bearer ${token}`,
				},
				credentials: "include",
			}
		);
		if (!response.ok)
			throw new Error(
				`Lỗi xóa cuộc trò chuyện: ${await response.text()}`
			);
		return { id: conversationId };
	},

	// Thêm chi tiết chat
	async addChatDetail(payload, conversationId, generatorIdMap) {
		const token = Cookies.get("access_token");
		if (!token) throw new Error("Không tìm thấy token xác thực");

		let finalConversationId = conversationId;
		if (!finalConversationId) {
			const newChat = await this.createConversation();
			finalConversationId = newChat.id;
		}

		const generatorId = generatorIdMap[payload.generator_id];
		if (!generatorId)
			throw new Error(
				`Không tìm thấy generator_id cho option ${payload.generator_id}`
			);

		const chatDetailPayload = {
			input_type: payload.input_type,
			input_text: payload.input_text,
			input_file_name: payload.input_file_name,
			input_file_path: null,
			output_type: payload.output_type,
			output_text: payload.output_text,
			output_image_url: payload.output_image_url,
			output_audio_url: payload.output_audio_url,
			output_video_url: payload.output_video_url,
			output_file_path: payload.output_file_url,
			output_file_name: payload.output_file_name,
			generator_id: generatorId,
		};

		const response = await fetch(
			`http://localhost:8000/chat-history/${finalConversationId}/add-detail`,
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Authorization: `Bearer ${token}`,
				},
				body: JSON.stringify(chatDetailPayload),
				credentials: "include",
			}
		);
		if (!response.ok)
			throw new Error(`Lỗi lưu chi tiết chat: ${await response.text()}`);
		return await response.json();
	},
};

export default ApiService;
