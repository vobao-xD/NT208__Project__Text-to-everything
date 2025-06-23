import { useContext, useRef } from "react";
import { ChatContext } from "@/context/ChatContext";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

const FileUpload = ({
	onFileSend,
	accept = ".mp3,.wav,.png,.jpg,.jpeg,.mp4,.webm,.pdf,.doc,.docx,.txt",
	disabled = false,
	selectedOption,
}) => {
	const { role } = useContext(ChatContext);
	const inputRef = useRef(null);
	const navigate = useNavigate();

	const getAcceptFormats = () => {
		switch (selectedOption) {
			case "1":
				return ".mp3,.wav";
			case "2":
				return ".png,.jpg,.jpeg";
			case "3":
				return ".mp4,.webm";
			case "4":
				return ".pdf,.doc,.docx,.txt";
			default:
				return (
					accept ||
					".mp3,.wav,.png,.jpg,.jpeg,.mp4,.webm,.pdf,.doc,.docx,.txt"
				);
		}
	};

	const handleFileChange = async (e) => {
		const file = e.target.files[0];
		if (file) {
			const data = {
				file,
				file_name: file.name,
				option: selectedOption,
			};
			onFileSend(null, data, selectedOption);
			if (inputRef.current) inputRef.current.value = "";
		}
	};

	return (
		<>
			<button
				onClick={() => {
					if (role === "free") {
						toast.error(
							"Tài khoản miễn phí không được phép upload!"
						);
						return;
					}
					inputRef.current.click();
				}}
				className={`upload-btn ${disabled ? "disabled" : ""}`}
				disabled={disabled}
			>
				+
			</button>
			<input
				type="file"
				accept={getAcceptFormats()}
				style={{ display: "none" }}
				ref={inputRef}
				onChange={handleFileChange}
				disabled={disabled}
			/>
		</>
	);
};

export default FileUpload;
