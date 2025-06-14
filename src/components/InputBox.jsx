import { useContext, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { ChatContext } from "@/context/ChatContext";
import FileUpload from "@/components/FileUpload";

const InputBox = () => {
	const { selectedOption, role, isLoading, sendMessage } =
		useContext(ChatContext);
	const [inputValue, setInputValue] = useState("");
	const [selectedFile, setSelectedFile] = useState(null);
	const [imagePreview, setImagePreview] = useState(null);
	const fileInputRef = useRef(null);

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

	// Placeholder
	const placeholder =
		selectedOption === "0"
			? "Mô tả những gì bạn muốn tạo, hoặc chọn file để phân tích (Video: .mp4/ Audio: .wav, .mp3/ File: .pdf, .doc, .docx, .txt/ Ảnh: .jpg, .jpeg, .png)"
			: selectedOption === "4"
			? "Hãy nhập lời thoại và chọn file tùy chỉnh (nếu có)"
			: "Mô tả những gì bạn muốn tạo ra";

	const handleSubmit = async () => {
		if (isLoading) return;

		// Validation
		if (fileOnlyOptions.includes(selectedOption)) {
			if (!selectedFile) {
				toast.error("Vui lòng chọn file để xử lý.", {
					closeButton: true,
					className:
						"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
				});
				return;
			}
		} else if (textOnlyOptions.includes(selectedOption)) {
			if (!inputValue.trim()) {
				toast.error("Vui lòng nhập nội dung trước khi gửi.", {
					closeButton: true,
					className:
						"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
				});
				return;
			}
		} else if (textAndFileOptions.includes(selectedOption)) {
			if (!inputValue.trim() && !selectedFile) {
				toast.error("Vui lòng nhập nội dung hoặc chọn file.", {
					closeButton: true,
					className:
						"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
				});
				return;
			}
		}

		// Kiểm tra role
		if (isFileUploadAllowed && selectedFile && role === "free") {
			toast.error("Tài khoản miễn phí không được phép upload file.", {
				closeButton: true,
				className:
					"p-0 w-[400px] border border-red-600/40 backdrop-blur-lg",
			});
			return;
		}

		await sendMessage(inputValue, selectedFile, selectedOption);
		setInputValue("");
		setSelectedFile(null);
		setImagePreview(null);
		if (fileInputRef.current) fileInputRef.current.value = "";
	};

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
			".jpg",
			".jpeg",
			".png",
		];
		if (
			file &&
			validExtensions.some((ext) => file.name.toLowerCase().endsWith(ext))
		) {
			setSelectedFile(file);
			if (
				[".jpg", ".jpeg", ".png"].some((ext) =>
					file.name.toLowerCase().endsWith(ext)
				)
			) {
				setImagePreview(URL.createObjectURL(file));
			} else {
				setImagePreview(null);
			}
		} else {
			toast.error(
				"File không hỗ trợ. Chọn .mp4, .wav, .mp3, .pdf, .doc, .docx, .txt, .jpg, .jpeg, .png."
			);
		}
	};

	const handleCancelFile = () => {
		setSelectedFile(null);
		setImagePreview(null);
		if (fileInputRef.current) fileInputRef.current.value = "";
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
						{isFileUploadAllowed && (
							<div className="upload-buttons">
								<button
									className={`file-upload-btn ${
										isLoading ? "disabled" : ""
									}`}
									onClick={() =>
										fileInputRef.current?.click()
									}
									disabled={isLoading}
									data-tooltip="Tải lên file (video, âm thanh, tài liệu, ảnh)"
								>
									<i className="fas fa-file-upload"></i>
								</button>
								<input
									type="file"
									ref={fileInputRef}
									onChange={handleFileSelect}
									style={{ display: "none" }}
									accept={
										selectedOption === "5"
											? ".jpg,.jpeg,.png"
											: selectedOption === "9" ||
											  selectedOption === "4"
											? ".wav,.mp3"
											: selectedOption === "10"
											? ".mp4"
											: selectedOption === "11"
											? ".pdf,.doc,.docx,.txt"
											: ".mp4,.wav,.mp3,.pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
									}
								/>
								{selectedFile && (
									<div className="file-info">
										{imagePreview ? (
											<div className="image-preview">
												<img
													src={imagePreview}
													alt="Preview"
												/>
												<button
													className="close-button"
													onClick={handleCancelFile}
												>
													<i className="fas fa-times"></i>
												</button>
											</div>
										) : (
											<div className="file-details">
												<span className="file-name">
													{selectedFile.name}
												</span>
												<button
													className="close-button"
													onClick={handleCancelFile}
												>
													<i className="fas fa-times"></i>
												</button>
											</div>
										)}
									</div>
								)}
							</div>
						)}
						{isTextInputAllowed && (
							<textarea
								className={`input ${
									isLoading ? "disabled" : ""
								}`}
								rows="3"
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
						{(isTextInputAllowed || isFileUploadAllowed) && (
							<div className="glow-wrapper">
								<button
									id="submit_btn"
									className={isLoading ? "disabled" : ""}
									onClick={handleSubmit}
									disabled={isLoading}
								>
									<i className="fas fa-paper-plane"></i>
								</button>
							</div>
						)}
					</>
				)}
			</div>
		</div>
	);
};

export default InputBox;
