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
			case "5":
				return "image";
			case "9":
				return "audio";
			case "10":
				return "video";
			case "11":
				return "file";
			default:
				return "text";
		}
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
				`Lỗi khi lấy thông tin người dùng: ${response.statusText}`
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
				`Lỗi khi lấy thông tin vai trò: ${response.statusText}`
			);
		return await response.json();
	},

	// Phân tích văn bản (cho mode 0 với text only)
	async analyzeText(text, email, role) {
		const response = await fetch("http://localhost:8000/analyze", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			credentials: "include",
			body: JSON.stringify({ user_text: text, email, role }),
		});
		if (!response.ok)
			throw new Error(`Lỗi phân tích: ${response.statusText}`);
		return response;
	},

	// Phân tích file (cho mode 0 với file only)
	async analyzeFile(file, email, role) {
		const formData = new FormData();
		formData.append("file", file);
		const response = await fetch("http://localhost:8000/analyze/file", {
			method: "POST",
			credentials: "include",
			body: formData,
		});
		if (!response.ok)
			throw new Error(`Lỗi phân tích file: ${response.statusText}`);
		return response;
	},

	// Phân tích cả text và file (cho mode 0 với cả hai)
	async analyzeTextAndFile(text, file, email, role) {
		const formData = new FormData();
		formData.append("text", text);
		formData.append("file", file);
		const response = await fetch(
			"http://localhost:8000/analyze/text-file",
			{
				method: "POST",
				credentials: "include",
				body: formData,
			}
		);
		if (!response.ok)
			throw new Error(
				`Lỗi phân tích text và file: ${response.statusText}`
			);
		return response;
	},

	// Xử lý text only (cho mode 1, 2, 3, 6, 7, 8)
	async processText(text, option, role) {
		let apiUrl, requestBody;
		const headers = { "Content-Type": "application/json" };

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
			credentials: "include",
			body: JSON.stringify(requestBody),
		});
		if (!response.ok)
			throw new Error(`Lỗi xử lý text: ${response.statusText}`);
		return response;
	},

	// Xử lý file only (cho mode 5, 9, 10, 11)
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
			credentials: "include",
			body: formData,
		});
		if (!response.ok)
			throw new Error(`Lỗi xử lý file: ${response.statusText}`);
		return response;
	},

	// Xử lý cả text và file (cho mode 4, và mode 0 khi có cả hai)
	async processTextAndFile(text, file, option, role) {
		if (!text || !file) throw new Error("Yêu cầu cả text và file!");
		if (option === "4" && !file.name.toLowerCase().endsWith(".wav"))
			throw new Error(
				"File phải có định dạng .wav cho Custom Text to Speech!"
			);

		const formData = new FormData();
		formData.append("text", text);
		formData.append("file", file);
		let apiUrl =
			role === "pro" && option === "4"
				? "http://localhost:8000/advanced/text-file"
				: "http://localhost:8000/text-file";

		const response = await fetch(apiUrl, {
			method: "POST",
			credentials: "include",
			body: formData,
		});
		if (!response.ok)
			throw new Error(`Lỗi xử lý text và file: ${response.statusText}`);
		return response;
	},

	// Chuẩn hóa phản hồi bot
	async normalizeBotMessage(response, option) {
		let botMessage = { type: "bot" };

		try {
			let data;
			if (option === "1" || option === "2" || option === "3") {
				// Lấy dữ liệu JSON từ response
				data = await response.json();
				const filePath = data.file_path; // Đường dẫn từ backend, ví dụ: "_outputs/23520146@gm.uit.edu.vn/..."
				botMessage.output_file_path = filePath;
				console.log(
					`normalize: bot content ${botMessage.output_file_path}`
				);
				const fileResponse = await fetch(
					`http://localhost:8000/get-output/${filePath}`,
					{
						method: "GET",
						credentials: "include",
					}
				);
				if (!fileResponse.ok)
					throw new Error(
						`Lỗi tải file: ${await fileResponse.text()}`
					);
				const blob = await fileResponse.blob();
				if (option === "1") {
					botMessage.content = {
						audio_url: URL.createObjectURL(blob),
					};
					botMessage.isAudio = true;
					botMessage.type = "audio";
				} else if (option === "2") {
					botMessage.content = {
						image_url: URL.createObjectURL(blob),
					};
					botMessage.isImage = true;
					botMessage.type = "image";
				} else if (option === "3") {
					botMessage.content = {
						video_url: URL.createObjectURL(blob),
					};
					botMessage.isVideo = true;
					botMessage.type = "video";
				}
			} else {
				// Xử lý text trực tiếp từ response
				data = await response.json();
				botMessage.content = {
					text:
						(option === "8" &&
							(typeof data.code === "object"
								? JSON.stringify(data.code)
								: data.code)) ||
						data.text ||
						data.response ||
						data.answer ||
						data.content ||
						"",
				};
				botMessage.isText = true;
				botMessage.type = "text";
			}
			botMessage.option = option; // Thêm option để theo dõi
			return botMessage;
		} catch (error) {
			throw new Error(`Lỗi chuẩn hóa bot message: ${error.message}`);
		}
	},

	// Tạo tin nhắn người dùng cho file hoặc text
	async createUserMessage(input, option) {
		let message = { type: "user" };

		if (typeof input === "string") {
			// Trường hợp text only
			message.content = input;
			message.input_type = "text";
			message.isText = true;
		} else if (input instanceof File) {
			// Trường hợp file
			const fileExtension = input.name.split(".").pop().toLowerCase();
			const url = URL.createObjectURL(input);
			message.content = `Đã gửi ${
				["mp3", "wav"].includes(fileExtension)
					? "file audio"
					: fileExtension === "mp4"
					? "video"
					: ["pdf", "doc", "docx", "txt"].includes(fileExtension)
					? "file"
					: "ảnh"
			}: ${input.name}`;
			if (input.type.startsWith("image/") || option === "5") {
				message.isImage = true;
				message.image_url = url;
				message.input_type = "image";
			} else if (
				["mp3", "wav"].includes(fileExtension) ||
				option === "9"
			) {
				message.isAudio = true;
				message.audio_url = url;
				message.input_type = "audio";
			} else if (fileExtension === "mp4" || option === "10") {
				message.isVideo = true;
				message.video_url = url;
				message.input_type = "video";
			} else if (
				["pdf", "doc", "docx", "txt"].includes(fileExtension) ||
				option === "11"
			) {
				message.isFile = true;
				message.file_url = url;
				message.fileName = input.name;
				message.input_type = "file";
			}
		} else {
			throw new Error("Đầu vào không hợp lệ: Phải là text hoặc file!");
		}

		message.option = option; // Thêm option để theo dõi
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

		return data.map((c) => ({
			id: c.id,
			title:
				(c.details[0]?.input_text ?? "Cuộc trò chuyện mới").substring(
					0,
					30
				) + (c.details[0]?.input_text?.length > 30 ? "..." : ""),
			created_at: c.created_at, // Thêm created_at để đồng bộ
			messages: c.details || [],
		}));
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
			const firstPrompt = messages[0]?.content ?? "Cuộc trò chuyện mới";
			title =
				firstPrompt.length > 30
					? `${firstPrompt.substring(0, 30)}...`
					: firstPrompt;
		}
		return {
			id: conversationId,
			title,
			created_at: data.created_at,
			messages: [],
		};
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

		const details = data.details || [];
		for (let detail of details) {
			const userMsg = {
				type: "user",
				content:
					detail.input_text ||
					(detail.input_file_name
						? `[Đã gửi tệp: ${detail.input_file_name}]`
						: "[Tin nhắn rỗng]"),
				isText: detail.input_type === "text",
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
				created_at: detail.created_at, // Thêm created_at
			};
			messages.push(userMsg);

			const botMsg = {
				type: "bot",
				content: {
					text: detail.output_text || null,
					image_url: detail.output_file_path || null, // Sửa để khớp với output_file_path
					audio_url: detail.output_file_path || null, // Sửa để khớp với output_file_path
					video_url: detail.output_file_path || null, // Sửa để khớp với output_file_path
					file_url: detail.output_file_path || null,
					file_name: detail.output_file_name || null,
				},
				isText: detail.output_type === "text",
				isAudio: detail.output_type === "audio",
				isImage: detail.output_type === "image",
				isVideo: detail.output_type === "video",
				isFile: detail.output_type === "file",
				option:
					Object.keys(generatorIdMap).find(
						(key) => generatorIdMap[key] === detail.generator_id
					) || null,
				created_at: detail.created_at, // Thêm created_at
			};
			messages.push(botMsg);
		}

		const firstDetail = details[0] || {};
		const title = firstDetail.input_text
			? firstDetail.input_text.length > 30
				? `${firstDetail.input_text.substring(0, 30)}...`
				: firstDetail.input_text
			: "Cuộc trò chuyện mới";

		return {
			id: conversationId,
			title,
			created_at: data.created_at, // Thêm created_at
			messages,
		};
	},

	// Xóa cuộc trò chuyện
	async deleteChatHistory(historyId) {
		const response = await fetch(
			`http://localhost:8000/chat-history/${historyId}`,
			{
				method: "DELETE",
				credentials: "include",
			}
		);
		if (!response.ok)
			throw new Error(`Lỗi xóa cuộc trò chuyện: ${response.statusText}`);
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
			input_type: payload.input_type || "text",
			input_text: payload.input_text || "",
			input_file_name: payload.input_file_name || null,
			input_file_path: payload.input_file_path || null,
			output_type: payload.output_type || null,
			output_text: payload.output_text || null,
			output_file_name: payload.output_file_name || null,
			output_file_path: payload.output_file_url || null,
			generator_id: generatorId,
		};

		const response = await fetch(
			`http://localhost:8000/chat-history/${finalConversationId}/add-detail`,
			{
				method: "POST",
				headers: { "Content-Type": "application/json" },
				credentials: "include",
				body: JSON.stringify(chatDetailPayload),
			}
		);
		if (!response.ok)
			throw new Error(`Lỗi lưu chi tiết chat: ${await response.text()}`);
		return await response.json();
	},
};

export default ApiService;
