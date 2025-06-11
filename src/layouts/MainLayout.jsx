import React, { useState } from "react";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import ChatBox from "../components/ChatBox";
import InputBox from "../components/InputBox";

const MainLayout = () => {
	const [selectedOption, setSelectedOption] = useState("1");
	const [messages, setMessages] = useState([]);

	const handleMessageSend = (text, data, option) => {
		// Add user message
		setMessages((prev) => [...prev, { type: "user", content: text }]);

		// Add bot response based on option
		switch (option) {
			case "1": // Audio
				setMessages((prev) => [
					...prev,
					{
						type: "bot",
						content: data.audio_url,
						isAudio: true,
					},
				]);
				break;
			case "2": // Image
				setMessages((prev) => [
					...prev,
					{
						type: "bot",
						content: data.image_url, // Thay image_base64 bằng image_url
						isImage: true,
					},
				]);
				break;
			case "3": // Video
				setMessages((prev) => [
					...prev,
					{
						type: "bot",
						content: data.video_url,
						isVideo: true,
					},
				]);
				break;
			case "4": // File
				setMessages((prev) => [
					...prev,
					{
						type: "bot",
						content: data.file_url,
						fileName: data.file_name || "downloaded_file",
						isFile: true,
					},
				]);
				break;
			default: // Text
				setMessages((prev) => [
					...prev,
					{
						type: "bot",
						content: data.text || "Default response",
						isText: true,
					},
				]);
				break;
		}
	};

	return (
		<div className="full-container">
			<Sidebar
				selectedOption={selectedOption}
				onOptionChange={setSelectedOption}
			/>
			<div className="content">
				<Header selectedOption={selectedOption} />
				<ChatBox messages={messages} />
				<InputBox
					selectedOption={selectedOption}
					onMessageSend={handleMessageSend}
				/>
			</div>
		</div>
	);
};

export default MainLayout;
