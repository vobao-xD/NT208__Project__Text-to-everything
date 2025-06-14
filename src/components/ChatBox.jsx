import { useContext } from "react";
import { ChatContext } from "@/context/ChatContext";
import { toast } from "react-toastify";

const ChatBox = () => {
	const { messages } = useContext(ChatContext);

	return (
		<div className="conversation content-item">
			{messages.map((message) => (
				<div
					key={message.id}
					className={`message ${message.type}-message ${
						message.isAudio ? "audio-message" : ""
					} ${message.isImage ? "image-message" : ""} ${
						message.isVideo ? "video-message" : ""
					} ${message.isFile ? "file-message" : ""}`}
				>
					{message.isText ? (
						<p className="text-message">{message.content}</p>
					) : message.isAudio ? (
						<audio
							controls
							src={
								message.content?.audio_url || message.audio_url
							}
							onError={() => toast.error("Không thể tải audio.")}
						/>
					) : message.isImage ? (
						<img
							src={
								message.content?.image_url || message.image_url
							}
							style={{ maxWidth: "100%" }}
							onError={() =>
								toast.error("Không thể tải hình ảnh.")
							}
						/>
					) : message.isVideo ? (
						<video
							controls
							style={{ maxWidth: "100%" }}
							onError={() => toast.error("Không thể tải video.")}
						>
							<source
								src={
									message.content?.video_url ||
									message.video_url
								}
								type="video/mp4"
							/>
							Your browser does not support the video tag.
						</video>
					) : message.isFile ? (
						<a
							href={message.content?.file_url || message.file_url}
							download={
								message.content?.fileName ||
								message.fileName ||
								"file"
							}
							className="file-link"
						>
							Download:{" "}
							{message.content?.fileName ||
								message.fileName ||
								"File"}
						</a>
					) : (
						<p>{message.content}</p>
					)}
				</div>
			))}
		</div>
	);
};

export default ChatBox;
