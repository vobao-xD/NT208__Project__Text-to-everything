import { useContext, useState } from "react";
import { ChatContext } from "@/context/ChatContext";
import FileUpload from "@/components/FileUpload";
import { toast } from "react-toastify";

const InputBox = () => {
	const { selectedOption, sendMessage, isLoading, isRateLimited } =
		useContext(ChatContext);
	const [inputText, setInputText] = useState("");

	const handleSubmit = async () => {
		if (isRateLimited || isLoading) {
			toast.error(
				"Hết lượt miễn phí hoặc đang xử lý. Vui lòng thử lại sau."
			);
			return;
		}
		if (
			!inputText.trim() &&
			!["5", "9", "10", "11"].includes(selectedOption)
		) {
			toast.error("Vui lòng nhập nội dung trước khi gửi.");
			return;
		}
		await sendMessage(inputText, null, selectedOption);
		setInputText("");
	};

	const handleFileSend = async (text, data, option) => {
		if (isRateLimited || isLoading) {
			toast.error(
				"Hết lượt miễn phí hoặc đang xử lý. Vui lòng thử lại sau."
			);
			return;
		}
		await sendMessage(null, data.file, option);
	};

	return (
		<div className="footer_content content-item">
			<div id="btn_complex">
				{["5", "9", "10", "11"].includes(selectedOption) ? (
					<div className="file-upload-container">
						<FileUpload
							onFileSend={handleFileSend}
							accept={
								selectedOption === "5"
									? ".jpg,.png,.jpeg"
									: selectedOption === "9"
									? ".mp3,.wav"
									: selectedOption === "10"
									? ".mp4,.webm"
									: ".pdf,.doc,.docx,.txt"
							}
							disabled={isLoading || isRateLimited}
							selectedOption={selectedOption}
						/>
						<span>
							{selectedOption === "5"
								? "Chọn file ảnh (.jpg, .png, .jpeg)..."
								: selectedOption === "9"
								? "Chọn file audio (.mp3, .wav)..."
								: selectedOption === "10"
								? "Chọn file video (.mp4, .webm)..."
								: "Chọn file (.pdf, .doc, .docx, .txt)..."}
						</span>
					</div>
				) : (
					<>
						<textarea
							value={inputText}
							onChange={(e) => setInputText(e.target.value)}
							className={`input ${isLoading ? "disabled" : ""}`}
							rows="4"
							placeholder="Mô tả những gì bạn muốn tạo..."
							disabled={isLoading || isRateLimited}
						/>
						<div className="input-actions">
							<FileUpload
								onFileSend={handleFileSend}
								selectedOption={selectedOption}
								disabled={isLoading || isRateLimited}
							/>
							<button
								id="submit_btn"
								onClick={handleSubmit}
								disabled={isLoading || isRateLimited}
							>
								Create
							</button>
						</div>
					</>
				)}
			</div>
		</div>
	);
};

export default InputBox;
