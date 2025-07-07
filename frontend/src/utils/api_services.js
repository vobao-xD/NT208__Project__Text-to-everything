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
				return "audio";
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
	async analyzeText(text,role) {
		if (role === "pro") {
        const formData = new FormData();
        formData.append("text", text); // Chỉ cần append text là đủ
        const response = await fetch(
            "http://localhost:8000/advanced/analyze",
            {
                method: "POST",
                credentials: "include",
                body: formData, 
            }
        );
		if (!response.ok)
			throw new Error(`Lỗi phân tích: ${response.statusText}`);
		return response;
}		else{

		const response = await fetch("http://localhost:8000/analyze", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			credentials: "include",
			body: JSON.stringify({ user_text: text }),
		});
		if (!response.ok)
			throw new Error(`Lỗi phân tích: ${response.statusText}`);
		return response;
	}},

	// Phân tích file (cho mode 0 với file only)
	async analyzeFile(file) {
		const formData = new FormData();
		formData.append("file", file);
		if (role === "pro") {
        const formData = new FormData();
        formData.append("text", text); // Chỉ cần append text là đủ
        const response = await fetch(
            "http://localhost:8000/advanced/analyze",
            {
                method: "POST",
                credentials: "include",
                body: formData, 
            }
        );
		if (!response.ok)
			throw new Error(`Lỗi phân tích: ${response.statusText}`);
		return response;
}else{
		const response = await fetch("http://localhost:8000/advanced/analyze", {
			method: "POST",
			credentials: "include",
			body: formData,
		});
		if (!response.ok)
			throw new Error(`Lỗi phân tích file: ${response.statusText}`);
		return response;
	}},

	// Phân tích cả text và file (cho mode 0 với cả hai)
	async analyzeTextAndFile(text, file,role) {
		const formData = new FormData();
		formData.append("text", text);
		formData.append("file", file);
		if (role === "pro") {
        const formData = new FormData();
        formData.append("text", text); // Chỉ cần append text là đủ
        const response = await fetch(
            "http://localhost:8000/advanced/analyze",
            {
                method: "POST",
                credentials: "include",
                body: formData, 
            }
        );
		if (!response.ok)
			throw new Error(`Lỗi phân tích: ${response.statusText}`);
		return response;
}else{
		const response = await fetch("http://localhost:8000/advanced/analyze", {
			method: "POST",
			credentials: "include",
			body: formData,
		});
		if (!response.ok)
			throw new Error(
				`Lỗi phân tích text và file: ${response.statusText}`
			);
		return response;
	}},

	// Xử lý text only (cho mode 1, 2, 3, 6, 7, 8)
	async processText(text, option, role) {
		const headers = { "Content-Type": "application/json" };

		let apiUrl, requestBody;

		switch (option) {
			case "1": // Text to Speech
				apiUrl =
					role === "pro"
						? "http://localhost:8000/advanced/text-to-audio"
						: "http://localhost:8000/text-to-speech/default";
				requestBody =
					role === "pro"
						? {
							text: text,
							voice: "alloy",
							model: "gpt-4o-mini-tts",
							response_format: "mp3",
							speed: 1,
							instructions:
								"sound like human, speak Vietnamese",
						}
						: {
							text: text,
							language: "Tiếng Việt",
							gender: "male",
							style: "default",
						};
				break;

			case "2": // Text to Image
				apiUrl =
					role === "pro"
						? "http://localhost:8000/advanced/text-to-image"
						: "http://localhost:8000/text-to-image";
				requestBody =
					role === "pro"
						? {
							model: "dall-e-3",
							prompt: text,
							n: 1,
							size: "1024x1024",
							quality: "standard",
							style: "vivid",
							response_format: "url",
						}
						: {
							prompt: text,
							steps: 4,
						};
				break;

			case "3": // Text to Video
				// Chỉ làm text to video API free, vì không đủ credit cho OpenAI :))
				if (role !== "pro") {
					toast.error(
						"Chỉ tài khoản Pro được phép sử dụng Text to Video!"
					);
					return;
				}
				apiUrl = "http://localhost:8000/text-to-video";
				requestBody = {
					prompt: text,
					guidance_scale: 5.0,
					fps: 16,
					steps: 30,
					frames: 64,
				};
				break;

			case "6": // Chatbot Content
				apiUrl =
					role === "pro"
						? "http://localhost:8000/advanced/chatbot-content"
						: "http://localhost:8000/chatbot/content";
				requestBody =
					role === "pro"
						? {
							user_input: text,
							history: [],
							system_prompt:
								"You are a helpful and friendly chatbot. You will give as much detail as possible within a very short sentence.",
							max_tokens: 500,
						}
						: {
							user_input: text,
							history: [],
							system_prompt:
								"You are a helpful and friendly chatbot. You will give as much detail as possible within a very short sentence.",
							max_tokens: 250,
						};
				break;

			case "7": // Generate Answer
				apiUrl =
					role === "pro"
						? "http://localhost:8000/advanced/generate-answer"
						: "http://localhost:8000/generate_answer";
				requestBody =
					role === "pro"
						? {
							question: text,
							context: "none",
							max_tokens: 500,
						}
						: {
							question: text,
						};
				break;

			case "8": // Text to Code
				apiUrl =
					role === "pro"
						? "http://localhost:8000/advanced/text-to-code"
						: "http://localhost:8000/text-to-code";
				requestBody =
					role === "pro"
						? {
							prompt: text,
							language: "python",
							max_tokens: 250,
						}
						: {
							prompt: text,
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
		if (!response.ok) {
			throw new Error(`Lỗi xử lý text: ${response.statusText}`);
		}
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

	// Xử lý cả text và file (cho mode 0 và mode 4)
	async processTextAndFile(text, file, option, role) {
		if (!text || !file) throw new Error("Yêu cầu cả text và file!");
		if (option === "4" && !file.name.toLowerCase().endsWith(".wav"))
			throw new Error(
				"File phải có định dạng .wav cho Custom Text to Speech!"
			);

		let apiUrl, formData;

		switch (option) {
			case "0": // Smart file and text to answer
				formData = new FormData();
				formData.append("text", text);
				formData.append("file", file);
				apiUrl =
					role === "pro"
						? "http://localhost:8000/advanced/file-text-to-answer"
						: "http://localhost:8000/advanced/file-text-to-answer"; // Mode 0 chỉ có trên advanced, cần kiểm tra backend
				// Thêm tham số tùy chọn (có thể điều chỉnh dựa trên nhu cầu)
				formData.append("vision_model_override", "gpt-4o");
				formData.append("detail_vision", "auto");
				formData.append("max_tokens_vision", "300");
				formData.append("assistant_model_override", "gpt-4o");
				break;

			case "4": // Custom Text to Speech with voice cloning
				if (role !== "pro")
					throw new Error(
						"Chỉ tài khoản Pro được phép sử dụng Custom Text to Speech!"
					);
				formData = new FormData();
				formData.append("text", text);
				formData.append("file", file);
				formData.append("language", "Tiếng Việt"); // Giá trị mặc định
				formData.append("use_existing_reference", "false"); // Giá trị mặc định
				apiUrl = "http://localhost:8000/text-to-speech/custom";
				break;

			default:
				throw new Error("Tính năng không được hỗ trợ!");
		}

		const response = await fetch(apiUrl, {
			method: "POST",
			credentials: "include",
			body: formData,
		});
		if (!response.ok) {
			throw new Error(`Lỗi xử lý text và file: ${response.statusText}`);
		}
		return response;
	},

	// api_services.js
	async saveOutputFile(userEmail, generatorName, fileContent, fileExtension) {
		const token = Cookies.get("access_token");
		if (!token) throw new Error("Không tìm thấy token xác thực");

		const response = await fetch("http://localhost:8000/save-output-file", {
			method: "POST",
			headers: {
				Authorization: `Bearer ${token}`,
			},
			credentials: "include",
			body: JSON.stringify({
				user_email: userEmail,
				generator_name: generatorName,
				file_content: Array.from(fileContent), // Chuyển Uint8Array thành array
				file_extension: fileExtension,
			}),
		});

		if (!response.ok)
			throw new Error(`Lỗi lưu file: ${await response.text()}`);
		const data = await response.json();
		return Path(data.file_path); // Giả định backend trả về đường dẫn
	},

	// Chuẩn hóa phản hồi bot
	async normalizeBotMessage(response, option) {
		let botMessage = { type: "bot", id: Date.now().toString() };

		try {
			const data = await response.json();
			botMessage.option = option;

			if (["0", "1", "2", "3", "4", "5"].includes(option)) {
				const filePath = data.file_paths ? data.file_paths[0] : data.file_path;
				if (!filePath)
					throw new Error("Không tìm thấy file_path trong response");
				
				const normalizedPath = filePath.replace(/\\/g, "/");

            
            	const relativePath = normalizedPath.startsWith("_outputs/")
					? normalizedPath.substring("_outputs/".length)
					: normalizedPath;

				botMessage.output_file_path = filePath;
				botMessage.output_file_name = filePath.split("/").pop(); 
				alert(relativePath);
				const fileResponse = await fetch(
					`http://localhost:8000/get-output/${relativePath}`,
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

				switch (option) {
					case "0": // File and text to answer (text output)
						botMessage.content = {
							text: data.answer || data.response || "",
						};
						botMessage.output_type = "text";
						botMessage.isText = true;
						break;
					case "1": // Text to audio
					case "4": // Custom text to speech
						botMessage.content = {
							audio_url: URL.createObjectURL(blob),
						};
						botMessage.output_type = "audio";
						botMessage.isAudio = true;
						break;
					case "2": // Text to image
					case "5": // Image processing
						botMessage.content = {
							image_url: URL.createObjectURL(blob),
						};
						botMessage.output_type = "image";
						botMessage.isImage = true;
						break;
					case "3": // Text to video
						botMessage.content = {
							video_url: URL.createObjectURL(blob),
						};
						botMessage.output_type = "video";
						botMessage.isVideo = true;
						break;
				}
			} else if (["6", "7", "8"].includes(option)) {
				botMessage.content = {
					text:
						(option === "8" && typeof data.code === "object"
							? JSON.stringify(data.code)
							: data.code) ||
						data.text ||
						data.response ||
						data.answer ||
						data.content ||
						"",
				};
				botMessage.output_type = "text";
				botMessage.isText = true;
			} else {
				throw new Error("Option không được hỗ trợ!");
			}

			return botMessage;
		} catch (error) {
			throw new Error(`Lỗi chuẩn hóa bot message: ${error.message}`);
		}
	},

	// Tạo tin nhắn người dùng cho file hoặc text
	async createUserMessage(input, option, userEmail) {
		let message = { type: "user" };

		if (typeof input === "string") {
			message.input_type = "text";
			message.input_text = input;
			message.content = input; // Giữ content cho hiển thị
			message.isText = true;
		} else if (input instanceof File) {
			const fileExtension = input.name.split(".").pop().toLowerCase();
			const fileTypes = {
				audio: ["mp3", "wav"],
				image: ["png", "jpg", "jpeg"],
				video: ["mp4", "avi", "mov"],
				file: ["pdf", "txt", "doc", "docx"],
			};

			let inputType = null;
			for (const [type, extensions] of Object.entries(fileTypes)) {
				if (extensions.includes(fileExtension)) {
					inputType = type;
					break;
				}
			}
			if (!inputType)
				throw new Error("Định dạng file không được hỗ trợ!");

			// Lưu file lên backend
			const fileContent = await input.arrayBuffer(); // Chuyển file thành bytes
			const savePath = await ApiService.saveOutputFile(
				userEmail,
				"user_upload", // Tên generator cho file upload
				new Uint8Array(fileContent),
				fileExtension
			);
			const filePath = savePath.toString().replace("./", "backend/"); // Thay đổi đường dẫn cho phù hợp

			message.input_type = inputType;
			message.input_file_path = filePath;
			message.input_file_name = input.name; // Optional, nhưng vẫn gán
			message.content = `Đã gửi ${inputType}: ${input.name}`;
			message[
				`is${inputType.charAt(0).toUpperCase() + inputType.slice(1)}`
			] = true;
			message[`${inputType}_url`] = filePath; // Sử dụng filePath cho URL tạm thời (sẽ gọi /get-output sau)
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
			"http://localhost:8000/chat-history?limit=10",
			{
				method: "GET",
				headers: { "Content-Type": "application/json" },
				credentials: "include",
			}
		);
		if (!response.ok)
			throw new Error(`Lỗi tải lịch sử chat: ${await response.text()}`);
		const data = await response.json();

		return data.map((c) => ({
			id: c.id,
			title:
				(Array.isArray(c.chat_details) && c.chat_details[0]?.input_text
					? c.chat_details[0].input_text.substring(0, 30) +
					(c.chat_details[0].input_text.length > 30 ? "..." : "")
					: "Cuộc trò chuyện mới"),
			created_at: c.created_at, // Thêm created_at để đồng bộ
			messages: c.chat_details || [],
		}));
	},

	// Tạo cuộc trò chuyện mới
	async createConversation(messages = []) {
		const token = Cookies.get("access_token");
		if (!token) throw new Error("Không tìm thấy token xác thực");
		const response = await fetch("http://localhost:8000/chat-history", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
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

	async getConversation(conversationId, generatorIdMap) {
		const token = Cookies.get("access_token");
		if (!token) throw new Error("Không tìm thấy token xác thực");

		const response = await fetch(
			`http://localhost:8000/chat-history/${conversationId}`,
			{
				method: "GET",
				headers: { "Content-Type": "application/json" },
				credentials: "include",
			}
		);
		if (!response.ok)
			throw new Error(
				`Lỗi tải cuộc trò chuyện: ${await response.text()}`
			);

		const data = await response.json();
		console.log("Raw response from /chat-history:", data);
		const messages = [];

		const chat_details = data.chat_details || [];
		for (let detail of chat_details) {
			// Always push user message first
			messages.push({
				id: detail.id + "_user",
				type: "user",
				content: detail.input_text || (detail.input_file_name ? `[Đã gửi tệp: ${detail.input_file_name}]` : "[Tin nhắn rỗng]"),
				isText: detail.input_type === "text",
				isAudio: detail.input_type === "audio",
				isImage: detail.input_type === "image",
				isVideo: detail.input_type === "video",
				isFile: detail.input_type === "file",
				audio_url: detail.input_type === "audio" ? `http://localhost:8000/get-output/${detail.input_file_path}` : null,
				image_url: detail.input_type === "image" ? `http://localhost:8000/get-output/${detail.input_file_path}` : null,
				video_url: detail.input_type === "video" ? `http://localhost:8000/get-output/${detail.input_file_path}` : null,
				file_url: detail.input_type === "file" ? `http://localhost:8000/get-output/${detail.input_file_path}` : null,
				input_file_name: detail.input_file_name || null,
				input_file_path: detail.input_file_path || null,
				created_at: detail.created_at,
			});

			// Then push bot message if output exists
			if (detail.output_text || detail.output_file_path) {
				messages.push({
					id: detail.id + "_bot",
					type: "bot",
					content: {
						text: detail.output_text || null,
						audio_url: detail.output_type === "audio" ? `http://localhost:8000/get-output/${detail.output_file_path}` : null,
						image_url: detail.output_type === "image" ? `http://localhost:8000/get-output/${detail.output_file_path}` : null,
						video_url: detail.output_type === "video" ? `http://localhost:8000/get-output/${detail.output_file_path}` : null,
						file_url: detail.output_type === "file" ? `http://localhost:8000/get-output/${detail.output_file_path}` : null,
						file_name: detail.output_file_name || null,
					},
					isText: detail.output_type === "text",
					isAudio: detail.output_type === "audio",
					isImage: detail.output_type === "image",
					isVideo: detail.output_type === "video",
					isFile: detail.output_type === "file",
					option: Object.keys(generatorIdMap).find((key) => generatorIdMap[key] === detail.generator_id) || null,
					output_file_path: detail.output_file_path || null,
					created_at: detail.created_at,
				});
			}
		}

		console.log("Prepared messages:", messages);
		const firstDetail = chat_details[0] || {};
		const title =
			firstDetail.input_text && firstDetail.input_text.length > 30
				? `${firstDetail.input_text.substring(0, 30)}...`
				: firstDetail.input_text || "Cuộc trò chuyện mới";

		return {
			id: conversationId,
			title,
			created_at: data.created_at,
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
			output_file_path: payload.output_file_path || null,
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
