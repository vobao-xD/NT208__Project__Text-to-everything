import { toast } from "react-toastify";
import { useContext, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import FileUpload from "@/components/FileUpload";
import { ChatContext } from "@/context/ChatContext";

const FreeAccountNotice = ({ navigate }) => (
	<div className="free-account-notice">
		<span className="notice-text">
			Tài khoản miễn phí không được phép upload. Vui lòng nâng cấp lên
			Plus hoặc Pro để sử dụng tính năng này!
		</span>
		<div className="fixed-button-container-2">
			<button
				className="rainbow-button"
				onClick={() => navigate("/advanced")}
			>
				Nâng cấp ngay
			</button>
		</div>
	</div>
);

const InputBox = () => {
	const { selectedOption, sendMessage, isLoading, isRateLimited, role } =
		useContext(ChatContext);
	const [inputText, setInputText] = useState("");
	const [inputValue, setInputValue] = useState("");
	const [selectedFile, setSelectedFile] = useState(null);
	const [imagePreview, setImagePreview] = useState(null);
	const fileInputRef = useRef(null);
	const imageInputRef = useRef(null);

	// Danh sách mode
	const textAndFileOptions = ["0", "4"];
	const fileOnlyOptions = ["5", "9", "10", "11"];
	const textOnlyOptions = ["1", "2", "3", "6", "7", "8"];
	const isTextInputAllowed =
		textAndFileOptions.includes(selectedOption) ||
		textOnlyOptions.includes(selectedOption);
	const isFileUploadAllowed =
		textAndFileOptions.includes(selectedOption) ||
		fileOnlyOptions.includes(selectedOption);

	const placeholder =
		selectedOption === "0"
			? "Mô tả những gì bạn muốn tạo, hoặc chọn file để phân tích (Video: .mp4/ Audio: .wav, .mp3/ File: .pdf, .doc, .docx, .txt)"
			: selectedOption === "1" || selectedOption === "4"
			? "Hãy nhập lời thoại của bạn"
			: "Mô tả những gì bạn muốn tạo ra";

	const handleFileSelect = (e) => {
		const file = e.target.files[0];
		const validExtensions = [
			".mp4",
			".wav",
			".mp3",
			".pdf",
			".doc",
			".docx",
			".txt",
		];
		if (
			file &&
			validExtensions.some((ext) => file.name.toLowerCase().endsWith(ext))
		) {
			setSelectedFile(file);
		} else {
			toast.error(
				"File không hỗ trợ. Chọn .mp4, .wav, .mp3, .pdf, .doc, .docx, .txt."
			);
		}
	};

	const handleSubmit = async () => {
		if (isLoading) {
			toast.error("Vui lòng chờ", {
				closeButton: true,
				className:
					"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
				ariaLabel: "Error",
			});
			return;
		}
		if (fileOnlyOptions.includes(selectedOption) && !selectedFile) {
			toast.error("Vui lòng chọn file để xử lý.", {
				closeButton: true,
				className:
					"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
				ariaLabel: "Error",
			});
			return;
		}
		if (textOnlyOptions.includes(selectedOption) && !inputValue.trim()) {
			toast.error("Vui lòng nhập nội dung trước khi gửi.", {
				closeButton: true,
				className:
					"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
				ariaLabel: "Error",
			});
			return;
		}
		if (
			textAndFileOptions.includes(selectedOption) &&
			!inputValue.trim() &&
			!selectedFile
		) {
			toast.error("Vui lòng nhập nội dung hoặc chọn file.", {
				closeButton: true,
				className:
					"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
				ariaLabel: "Error",
			});
			return;
		}

		await sendMessage(inputValue, selectedFile, selectedOption);
		setInputValue("");
		setSelectedFile(null);
		setImagePreview(null);
		if (fileInputRef.current) fileInputRef.current.value = "";
		if (imageInputRef.current) imageInputRef.current.value = "";
	};

	const handleImageSelect = (e) => {
		const file = e.target.files[0];
		const validExtensions = [".jpg", ".jpeg", ".png"];
		if (
			file &&
			validExtensions.some((ext) => file.name.toLowerCase().endsWith(ext))
		) {
			setSelectedFile(file);
			setImagePreview(URL.createObjectURL(file));
		} else {
			toast.error("File không hỗ trợ. Chọn .jpg, .jpeg, .png.");
		}
	};

	const handleFileSend = async (text, data, option) => {
		if (isRateLimited || isLoading) {
			toast.error(
				"Hết lượt miễn phí hoặc đang xử lý. Vui lòng thử lại sau."
			);
			return;
		}
		await sendMessage(text, data, option);
	};

	return (
		<div className="footer_content content-item">
			<div className="input-container">
				{fileOnlyOptions.includes(selectedOption) ? (
					<div className="file-upload-wrapper">
						<FileUpload
							onFileSend={(file) =>
								sendMessage(null, file, selectedOption)
							}
							accept={
								selectedOption === "5"
									? ".jpg,.jpeg,.png"
									: selectedOption === "9"
									? ".wav,.mp3"
									: selectedOption === "10"
									? ".mp4"
									: ".pdf,.doc,.docx,.txt"
							}
							disabled={isLoading}
						/>
						<span className="file-upload-hint">
							{selectedOption === "5" &&
								"Hãy chọn file ảnh (.jpg, .jpeg, .png) để cải thiện chất lượng..."}
							{selectedOption === "9" &&
								"Hãy chọn file (.wav, .mp3) để chuyển thành văn bản..."}
							{selectedOption === "10" &&
								"Hãy chọn file video (.mp4) để chuyển thành văn bản..."}
							{selectedOption === "11" &&
								"Hãy chọn file (.pdf, .doc, .docx, .txt) để chuyển thành văn bản..."}
						</span>
					</div>
				) : (
					<>
						{isTextInputAllowed && (
							<textarea
								className={`input ${
									isLoading ? "disabled" : ""
								} focus:border-blue-600`}
								rows="4"
								placeholder={placeholder}
								value={inputValue}
								onChange={(e) => setInputValue(e.target.value)}
								onKeyDown={(e) => {
									if (e.key === "Enter" && !e.shiftKey) {
										e.preventDefault();
										handleSubmit();
									}
								}}
								disabled={isLoading}
							/>
						)}
						{isFileUploadAllowed && selectedOption === "0" && (
							<div className="upload-buttons">
								<button
									className={`file-upload-btn ${
										isLoading ? "disabled" : ""
									}`}
									onClick={() =>
										fileInputRef.current?.click()
									}
									disabled={isLoading}
									data-tooltip="Nhập liệu bằng video, âm thanh, tài liệu"
								>
									+
								</button>
								<button
									className={`file-upload-btn ${
										isLoading ? "disabled" : ""
									}`}
									onClick={() =>
										imageInputRef.current?.click()
									}
									disabled={isLoading}
									data-tooltip="Đính kèm hình ảnh"
								>
									📎
								</button>
								<input
									type="file"
									ref={imageInputRef}
									onChange={handleImageSelect}
									style={{ display: "none" }}
									accept=".jpg,.jpeg,.png"
								/>
								<input
									type="file"
									ref={fileInputRef}
									onChange={handleFileSelect}
									style={{ display: "none" }}
									accept=".mp4,.wav,.mp3,.pdf,.doc,.docx,.txt"
								/>
								{imagePreview && (
									<div className="image-preview">
										<img src={imagePreview} alt="Preview" />
										<button
											className="close-button"
											onClick={() => {
												setSelectedFile(null);
												setImagePreview(null);
												if (imageInputRef.current)
													imageInputRef.current.value =
														"";
												if (fileInputRef.current)
													fileInputRef.current.value =
														"";
											}}
										>
											×
										</button>
									</div>
								)}
							</div>
						)}
						{(isTextInputAllowed || isFileUploadAllowed) && (
							<div className="glow-wrapper">
								<button
									id="submit_btn"
									className={isLoading ? "disabled" : ""}
									onClick={handleSubmit}
									disabled={isLoading}
								>
									Create
								</button>
							</div>
						)}
					</>
				)}
			</div>
		</div>
	);

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
							placeholder="Mô tả những gì bạn muốn tạo"
							disabled={isLoading || isRateLimited}
						/>
						<div className="input-actions">
							<FileUpload
								onFileSend={handleFileSend}
								disabled={isLoading || isRateLimited}
								selectedOption={selectedOption}
							/>
							<div className="glow-wrapper">
								<button
									id="submit_btn"
									className={isLoading ? "disabled" : ""}
									onClick={handleSubmit}
									disabled={isLoading || isRateLimited}
								>
									Create
								</button>
							</div>
						</div>
					</>
				)}
			</div>
		</div>
	);
};

export default InputBox;
