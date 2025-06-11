import React from "react";

const ChatBox = ({ messages }) => {
	return (
		<div className="conversation">
			{messages.map((message, index) => (
				<div
					key={index}
					className={`message ${
						message.type === "user" ? "user-message" : "bot-message"
					}`}
				>
					{message.isText ? (
						<p>{message.content}</p>
					) : message.isAudio ? (
						<audio
							controls
							src={message.content}
							onError={() => alert("Không thể tải audio.")}
						></audio>
					) : message.isImage ? (
						<img
							src={message.content} // Thay data:image/png;base64
							alt="Generated"
							style={{ maxWidth: "100%" }}
							onError={() => alert("Không thể tải hình ảnh.")}
						/>
					) : message.isVideo ? (
						<video
							controls
							style={{ maxWidth: "100%" }}
							onError={() => alert("Không thể tải video.")}
						>
							<source src={message.content} type="video/mp4" />
							Your browser does not support the video tag.
						</video>
					) : message.isFile ? (
						<a
							href={message.content}
							download={message.fileName || "downloaded_file"}
							style={{
								textDecoration: "underline",
								color: "#007bff",
							}}
						>
							Download: {message.fileName || "File"}
						</a>
					) : (
						<p>{message.content}</p> // Fallback
					)}
				</div>
			))}
		</div>
	);
};

export default ChatBox;
