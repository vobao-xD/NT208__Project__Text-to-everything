import React, { useState } from "react";
import FileUpload from "./FileUpload";

const InputBox = ({ selectedOption, onMessageSend }) => {
	const [inputText, setInputText] = useState("");

	const handleSubmit = async () => {
		if (!inputText.trim() && selectedOption !== "4") {
			alert("Vui lòng nhập nội dung trước khi gửi.");
			return;
		}

		try {
			let apiUrl;
			let requestBody = {};

			if (selectedOption === "1") {
				// Text to Speech
				apiUrl = "http://localhost:8000/text-to-speech";
				requestBody = {
					text: inputText,
					voice: "banmai",
					speed: "0",
				};
			} else if (selectedOption === "2") {
				// Text to Image
				apiUrl = "http://localhost:8000/text-to-image/quick";
				requestBody = {
					prompt: inputText,
					steps: 0,
				};
			} else if (selectedOption === "3") {
				// Text to Video
				apiUrl = "http://localhost:8000/text-to-video";
				requestBody = {
					prompt: inputText,
					duration: 5,
				};
			} else if (selectedOption === "4") {
				// Text
				onMessageSend(inputText, { text: inputText }, selectedOption);
				setInputText("");
				return;
			} else {
				alert("Tính năng này chưa được hỗ trợ!");
				return;
			}

			const response = await fetch(apiUrl, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(requestBody),
			});

			if (!response.ok) {
				throw new Error(
					`Lỗi API (${response.status}): ${await response.text()}`
				);
			}

			const data = await response.json();
			onMessageSend(
				inputText,
				{
					...data,
					image_url: selectedOption === "2" ? data.image_url : null, // Đảm bảo trả về image_url
				},
				selectedOption
			);
			setInputText("");

			if (selectedOption === "1") {
				const audio = new Audio(data.audio_url);
				audio.play();
			} else if (selectedOption === "2") {
				console.log("Image URL:", data.image_url);
			} else if (selectedOption === "3") {
				console.log("Video URL:", data.video_url);
			}
		} catch (error) {
			console.error("Lỗi:", error);
			alert("Có lỗi xảy ra khi gọi API: " + error.message);
		}
	};

	const handleFileSend = (text, data, option) => {
		onMessageSend(text, data, option);
	};

	return (
		<div className="footer_content">
			<div id="btn_complex">
				<textarea
					value={inputText}
					onChange={(e) => setInputText(e.target.value)}
					className="input"
					rows="4"
					placeholder="Mô tả những gì bạn muốn tạo"
					disabled={selectedOption === "4"}
				/>
				<div className="input-actions">
					<FileUpload
						onFileSend={handleFileSend}
						selectedOption={selectedOption}
					/>
					<button id="submit_btn" onClick={handleSubmit}>
						Create
					</button>
				</div>
			</div>
		</div>
	);
};

export default InputBox;
