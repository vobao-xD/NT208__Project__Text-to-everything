const detectInputFileType = (filename) => {
	const ext = filename.split(".").pop().toLowerCase();
	if (["mp3", "wav"].includes(ext)) return "audio";
	if (["png", "jpg", "jpeg"].includes(ext)) return "image";
	if (["mp4", "avi", "mov"].includes(ext)) return "video";
	if (["pdf", "txt", "doc", "docx"].includes(ext)) return "file";
	return "file";
};

const normalizeBotMessageContent = (botMessage) => {
	let outputText = null;
	if (botMessage.option === "8") {
		outputText =
			typeof botMessage.content.text === "object"
				? JSON.stringify(botMessage.content.text)
				: botMessage.content.text;
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
			: botMessage.content.file_url
			? "file"
			: "text",
		isText:
			!botMessage.content.image_url &&
			!botMessage.content.video_url &&
			!botMessage.content.audio_url &&
			!botMessage.content.file_url,
		isImage: !!botMessage.content.image_url,
		isVideo: !!botMessage.content.video_url,
		isAudio: !!botMessage.content.audio_url,
		isFile: !!botMessage.content.file_url,
		text: outputText,
		image_url: botMessage.content.image_url || null,
		video_url: botMessage.content.video_url || null,
		audio_url: botMessage.content.audio_url || null,
		file_url: botMessage.content.file_url || null,
		file_name: botMessage.content.file_name || null,
	};
};

const mapOptionToType = (option) => {
	switch (option) {
		case "1":
			return "audio";
		case "2":
			return "image";
		case "3":
			return "video";
		case "4":
			return "file";
		case "8":
			return "text";
		default:
			return "text";
	}
};

const prepareChatDetailPayload = (
	inputText,
	inputFileName,
	inputFile,
	normalizedContent,
	generatorId,
	selectedOption
) => {
	return {
		input_type: inputFileName
			? detectInputFileType(inputFileName)
			: mapOptionToType(selectedOption),
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
};

const addChatDetail = async (
	payload,
	currentConversationId,
	setCurrentConversationId,
	setConversations,
	conversations,
	generatorIdMap
) => {
	console.log(payload);
	try {
		const token = Cookies.get("access_token");
		if (!token) {
			toast.error("Không tìm thấy token xác thực", {
				closeButton: true,
				className:
					"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
				ariaLabel: "Error",
			});
			return;
		}

		let conversationId = currentConversationId;
		if (!conversationId) {
			const newChatResponse = await fetch(
				"http://localhost:8000/chat-history",
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({ chat_details: [] }),
					credentials: "include", // Gửi cookie
				}
			);

			if (!newChatResponse.ok) {
				throw new Error(
					`Lỗi tạo cuộc trò chuyện mới: ${await newChatResponse.text()}`
				);
			}

			const newChatData = await newChatResponse.json();
			conversationId = newChatData.id;
			setCurrentConversationId(conversationId);
		}

		// let fileUrl = payload.input_file_name
		// 	? payload.input_file_url
		// 	: null;
		// if (payload.input_file) {
		// 	const formData = new FormData();
		// 	formData.append("file", payload.input_file);
		// 	const uploadResponse = await fetch(
		// 		"http://localhost:8000/upload-file",
		// 		{
		// 			method: "POST",
		// 			body: formData,
		// 			credentials: "include", // Gửi cookie
		// 		}
		// 	);

		// 	if (!uploadResponse.ok) {
		// 		throw new Error(
		// 			`Lỗi upload file: ${await uploadResponse.text()}`
		// 		);
		// 	}

		// 	const uploadData = await uploadResponse.json();
		// 	fileUrl = uploadData.file_url;
		// }

		const generatorId = generatorIdMap[payload.generator_id];
		if (!generatorId) {
			throw new Error(
				`Không tìm thấy generator_id cho option ${payload.generator_id}`
			);
		}

		const chatDetailPayload = {
			input_type: payload.input_type,
			input_text: payload.input_text,
			input_file_name: payload.input_file_name,
			// input_file_path: fileUrl,
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
			`http://localhost:8000/chat-history/${conversationId}/add-detail`,
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(chatDetailPayload),
				credentials: "include", // Gửi cookie
			}
		);

		if (!response.ok) {
			throw new Error(`Lỗi lưu chi tiết chat: ${await response.text()}`);
		}

		const savedDetail = await response.json();
		console.log("Saved chat detail:", savedDetail);

		const updatedConversations = await fetch(
			"http://localhost:8000/chat-history?limit=50",
			{
				method: "GET",
				headers: {
					"Content-Type": "application/json",
				},
				credentials: "include", // Gửi cookie
			}
		).then((res) => res.json());

		setConversations(
			updatedConversations.map((c) => {
				const existingConversation = conversations.find(
					(existing) => existing.id === c.id
				);
				const title = existingConversation
					? existingConversation.title
					: (
							c.details[0]?.input_text || "Cuộc trò chuyện mới"
					  ).substring(0, 30) + "...";
				return {
					id: c.id,
					title,
					messages: c.details,
				};
			})
		);
	} catch (err) {
		console.error("addChatDetail error:", err);
		toast.error("Có lỗi xảy ra khi lưu chi tiết chat: " + err.message, {
			closeButton: true,
			className:
				"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
			ariaLabel: "Error",
		});
	}
};

const handleNewChat = async (
	setCurrentConversationId,
	setConversations,
	setChatHistory,
	chatHistory
) => {
	try {
		if (chatHistory.length <= 0) return;

		const token = Cookies.get("access_token");
		console.log(`Chat cookie: ${token}`);
		if (!token) {
			toast.error("Không tìm thấy token xác thực", {
				closeButton: true,
				className:
					"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
				ariaLabel: "Error",
			});
			return;
		}

		const response = await fetch("http://localhost:8000/chat-history", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ chat_details: [] }),
			credentials: "include",
		});

		if (!response.ok) {
			throw new Error(
				`Lỗi API (${response.status}): ${await response.text()}`
			);
		}

		const data = await response.json();
		const conversationId = data.id;

		if (chatHistory.length > 0) {
			const firstPrompt = chatHistory[0].content;
			const title =
				firstPrompt.length > 30
					? firstPrompt.substring(0, 30) + "..."
					: firstPrompt;
			setConversations((prev) => [
				...prev,
				{
					id: conversationId,
					messages: [...chatHistory],
					title,
				},
			]);
		}

		setCurrentConversationId(conversationId);
		setChatHistory([]);
	} catch (error) {
		console.error("Error:", error);
		toast.error(
			"Có lỗi xảy ra khi tạo cuộc trò chuyện mới: " + error.message,
			{
				closeButton: true,
				className:
					"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
				ariaLabel: "Error",
			}
		);
	}
};

const fetchChatHistories = async (setConversations) => {
	try {
		const token = Cookies.get("access_token");
		console.log(`Chat cookie: ${token}`);
		if (!token) {
			console.error("Không tìm thấy token xác thực");
			return;
		}

		const response = await fetch(
			"http://localhost:8000/chat-history?limit=50",
			{
				method: "GET",
				headers: {
					"Content-Type": "application/json",
				},
				credentials: "include", // Gửi cookie
			}
		);

		if (!response.ok) {
			throw new Error(
				`Lỗi API (${response.status}): ${await response.text()}`
			);
		}

		const data = await response.json();
		setConversations(
			data.map((c) => {
				const firstPrompt =
					c.details[0]?.input_text || "Cuộc trò chuyện mới";
				const title =
					firstPrompt.length > 30
						? firstPrompt.substring(0, 30) + "..."
						: firstPrompt;
				return {
					id: c.id,
					title,
					messages: c.details,
				};
			})
		);
	} catch (err) {
		console.error("fetchChatHistories error:", err);
		toast.error("Có lỗi xảy ra khi tải lịch sử chat: " + err.message, {
			closeButton: true,
			className:
				"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
			ariaLabel: "Error",
		});
	}
};

const loadConversation = async (
	conversationId,
	setChatHistory,
	setCurrentConversationId,
	generatorIdMap
) => {
	try {
		const token = Cookies.get("access_token");
		if (!token) {
			toast.error("Không tìm thấy token xác thực", {
				closeButton: true,
				className:
					"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
				ariaLabel: "Error",
			});
			return;
		}

		const response = await fetch(
			`http://localhost:8000/chat-history/${conversationId}`,
			{
				method: "GET",
				headers: {
					"Content-Type": "application/json",
				},
				credentials: "include", // Gửi cookie
			}
		);

		if (!response.ok) {
			throw new Error(
				`Lỗi API (${response.status}): ${await response.text()}`
			);
		}

		const data = await response.json();
		const messages = [];

		for (let detail of data.details) {
			const userMsg = {
				type: "user",
				content:
					detail.input_text ||
					`[Đã gửi tệp: ${detail.input_file_name || "File"}]`,
				isText: !detail.input_file_name,
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

		setChatHistory(messages);
		setCurrentConversationId(conversationId);
	} catch (err) {
		console.error("loadConversation error:", err);
		toast.error("Có lỗi xảy ra khi tải cuộc trò chuyện: " + err.message, {
			closeButton: true,
			className:
				"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
			ariaLabel: "Error",
		});
	}
};

const handleDeleteConversation = async (
	conversationId,
	currentConversationId,
	setConversations,
	setChatHistory,
	setCurrentConversationId
) => {
	const confirmDelete = window.confirm(
		"Bạn có chắc chắn muốn xóa đoạn chat này?"
	);
	if (!confirmDelete) return;

	try {
		const token = Cookies.get("access_token");
		if (!token) {
			toast.error("Không tìm thấy token xác thực", {
				closeButton: true,
				className:
					"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
				ariaLabel: "Error",
			});
			return;
		}

		const response = await fetch(
			`http://localhost:8000/chat-history/${conversationId}`,
			{
				method: "DELETE",
				headers: {
					"Content-Type": "application/json",
				},
				credentials: "include", // Gửi cookie
			}
		);

		if (!response.ok) {
			throw new Error(
				`Lỗi API (${response.status}): ${await response.text()}`
			);
		}

		setConversations((prev) => prev.filter((c) => c.id !== conversationId));
		if (conversationId === currentConversationId) {
			setChatHistory([]);
			setCurrentConversationId(null);
		}
	} catch (err) {
		console.error("Xoá chat lỗi:", err);
		toast.error("Có lỗi xảy ra khi xóa cuộc trò chuyện: " + err.message, {
			closeButton: true,
			className:
				"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
			ariaLabel: "Error",
		});
	}
};


	// Hàm tiện ích: Chuẩn bị payload cho chi tiết chat
	prepareChatDetailPayload(
		inputText,
		inputFile,
		normalizedContent,
		generatorId,
		selectedOption
	) {
		const inputFileName = inputFile ? inputFile.name : null;
		return {
			input_type: inputFileName
				? this.detectInputFileType(inputFileName)
				: this.mapOptionToType(selectedOption),
			input_text: inputFileName ? null : inputText,
			input_file_path: inputFileName ? `/uploads/${inputFileName}` : null,
			output_type:
				normalizedContent.fileType ||
				this.mapOptionToType(selectedOption),
			output_text: normalizedContent.isText
				? normalizedContent.content
				: null,
			output_image_url:
				normalizedContent.fileType === "image"
					? normalizedContent.content
					: null,
			output_audio_url:
				normalizedContent.fileType === "audio"
					? normalizedContent.content
					: null,
			output_video_url:
				normalizedContent.fileType === "video"
					? normalizedContent.content
					: null,
			output_file_path:
				normalizedContent.fileType === "file"
					? normalizedContent.content
					: null,
			output_file_name: normalizedContent.fileName || null,
			generator_id: generatorId,
		};
	},