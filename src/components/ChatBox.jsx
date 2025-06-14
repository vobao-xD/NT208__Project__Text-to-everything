import { useContext } from "react";
import { ChatContext } from "@/context/ChatContext";

const MessageContent = ({ message, isUser }) => {
	const mediaStyle = {
		width: "100%",
		maxWidth: isUser ? "300px" : "500px", // Khác biệt cho user/bot
		borderRadius: "10px",
	};

	const content = isUser ? message : message.content || {}; // Xử lý content undefined

	if (isUser ? message.isAudio : message.isAudio) {
		return (
			<audio
				controls
				src={isUser ? message.audio_url : content.audio_url}
				style={mediaStyle}
				onError={() => toast.error("Không thể tải audio.")}
			/>
		);
	}

	if (isUser ? message.isImage : message.isImage) {
		return (
			<img
				src={isUser ? message.image_url : content.image_url}
				alt={isUser ? "Ảnh đã gửi" : "Generated"}
				style={mediaStyle}
				onError={() => toast.error("Không thể tải hình ảnh.")}
			/>
		);
	}

	if (isUser ? message.isVideo : message.isVideo) {
		return (
			<video
				controls
				src={isUser ? message.video_url : content.video_url}
				style={mediaStyle}
				onError={() => toast.error("Không thể tải video.")}
			/>
		);
	}

	if (isUser ? message.isFile : message.isFile) {
		return (
			<a
				href={isUser ? message.file_url : content.file_url}
				download={
					isUser ? message.file_name : content.file_name || "file"
				}
				target="_blank"
				rel="noopener noreferrer"
				className="file-link"
				style={{
					display: "flex",
					alignItems: "center",
					gap: "8px",
				}}
			>
				<span style={{ fontSize: "24px" }}>📄</span>
				<span>
					{(isUser ? message.file_name : content.file_name) ||
						"Tệp đính kèm"}
				</span>
			</a>
		);
	}

	if (isUser ? message.isText : message.isText) {
		return (
			<p className="text-message">
				{isUser ? message.content : content.text}
			</p>
		);
	}

	return <p className="text-message">Tin nhắn không hỗ trợ</p>; // Fallback
};

const ChatBox = () => {
	const { messages, isLoading } = useContext(ChatContext);

	return (
		<div className="conversation content-item">
			{messages.map((message) => (
				<div
					key={message.id || message.content?.text || Date.now()}
					className={`message ${message.type}-message ${
						message.isAudio ? "audio-message" : ""
					} ${message.isImage ? "image-message" : ""} ${
						message.isVideo ? "video-message" : ""
					} ${message.isFile ? "file-message" : ""}`}
				>
					<MessageContent
						message={message}
						isUser={message.type === "user"}
					/>
				</div>
			))}
			{isLoading && <div className="loading-spinner"></div>}
		</div>
	);
};

export default ChatBox;
