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
	const [isRecording, setIsRecording] = useState(false);
	const fileInputRef = useRef(null);
	const mediaRecorderRef = useRef(null);
	const chunksRef = useRef([]);

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

	const startRecording = async () => {
		try {
			const stream = await navigator.mediaDevices.getUserMedia({
				audio: true,
			});
			mediaRecorderRef.current = new MediaRecorder(stream);
			chunksRef.current = [];
			mediaRecorderRef.current.ondataavailable = (e) =>
				chunksRef.current.push(e.data);
			mediaRecorderRef.current.onstop = async () => {
				const blob = new Blob(chunksRef.current, {
					type: "audio/webm",
				});
				stream.getTracks().forEach((track) => track.stop());
				if (selectedOption === "0") {
					try {
						const extractedText =
							await ApiService.extractTextFromMedia(blob, "9");
						setInputText(extractedText);
						toast.success("Đã trích xuất văn bản từ giọng nói.");
					} catch (error) {
						toast.error(
							"Lỗi trích xuất âm thanh: " + error.message
						);
					}
				} else if (selectedOption === "4") {
					try {
						const wavBlob = await convertWebmToWav(blob);
						const file = new File(
							[wavBlob],
							`voice_sample_${new Date()
								.toISOString()
								.replace(/[:.]/g, "-")}.wav`,
							{ type: "audio/wav" }
						);
						setSelectedFile(file);
						toast.success("Đã tạo file giọng mẫu .wav.");
					} catch (error) {
						toast.error(
							"Lỗi chuyển đổi sang .wav: " + error.message
						);
					}
				}
			};
			mediaRecorderRef.current.start();
			setIsRecording(true);
		} catch (error) {
			toast.error("Lỗi truy cập microphone: " + error.message);
		}
	};

	const stopRecording = () => {
		if (mediaRecorderRef.current && isRecording) {
			mediaRecorderRef.current.stop();
			setIsRecording(false);
		}
	};

	const convertWebmToWav = (webmBlob) => {
		return new Promise((resolve, reject) => {
			const reader = new FileReader();
			reader.onload = async (e) => {
				const audioContext = new (window.AudioContext ||
					window.webkitAudioContext)();
				const arrayBuffer = e.target.result;
				try {
					const audioBuffer = await audioContext.decodeAudioData(
						arrayBuffer
					);
					const wavData = audioBufferToWav(audioBuffer);
					resolve(new Blob([wavData], { type: "audio/wav" }));
				} catch (error) {
					reject(error);
				}
			};
			reader.onerror = () => reject(new Error("Lỗi đọc file WebM."));
			reader.readAsArrayBuffer(webmBlob);
		});
	};

	// Hàm chuyển AudioBuffer sang WAV
	const audioBufferToWav = (audioBuffer) => {
		const numChannels = audioBuffer.numberOfChannels;
		const sampleRate = audioBuffer.sampleRate;
		const length = audioBuffer.length * numChannels;
		const data = new Float32Array(length);
		audioBuffer.copyFromChannel(data, 0, 0);

		const buffer = new ArrayBuffer(44 + length * 2);
		const view = new DataView(buffer);

		// Header WAV
		writeString(view, 0, "RIFF");
		view.setUint32(4, 36 + length * 2, true);
		writeString(view, 8, "WAVE");
		writeString(view, 12, "fmt ");
		view.setUint32(16, 16, true);
		view.setUint16(20, 1, true); // PCM
		view.setUint16(22, numChannels, true);
		view.setUint32(24, sampleRate, true);
		view.setUint32(28, sampleRate * numChannels * 2, true);
		view.setUint16(32, numChannels * 2, true);
		view.setUint16(34, 16, true); // Bit depth
		writeString(view, 36, "data");
		view.setUint32(40, length * 2, true);

		// Dữ liệu âm thanh
		floatTo16BitPCM(view, 44, data);

		return buffer;
	};

	// Hàm hỗ trợ ghi dữ liệu WAV
	const writeString = (view, offset, string) => {
		for (let i = 0; i < string.length; i++) {
			view.setUint8(offset + i, string.charCodeAt(i));
		}
	};

	const floatTo16BitPCM = (output, offset, input) => {
		for (let i = 0; i < input.length; i++, offset += 2) {
			const s = Math.max(-1, Math.min(1, input[i]));
			output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
		}
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
								<button
									className={`file-upload-btn ${
										isRecording ? "recording" : ""
									}`}
									onClick={
										isRecording
											? stopRecording
											: startRecording
									}
									data-tooltip={
										isRecording
											? selectedOption === "0"
												? "Dừng nhập giọng"
												: "Dừng thu âm"
											: selectedOption === "0"
											? "Nhập bằng giọng nói"
											: "Thu âm giọng mẫu"
									}
								>
									<i
										className={`fas ${
											isRecording
												? "fa-stop"
												: "fa-microphone"
										}`}
									></i>
								</button>
								{selectedFile && (
									<div className="file-info">
										(
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
										)
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
