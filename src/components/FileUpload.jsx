import { useContext, useRef } from "react";
import { ChatContext } from "@/context/ChatContext";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

const FileUpload = ({ onFileSend, accept, disabled, selectedOption }) => {
	const { role } = useContext(ChatContext);
	const navigate = useNavigate();
	const inputRef = useRef(null);

	const getAcceptFormats = () => {
		switch (selectedOption) {
			case "5":
				return ".jpg,.png,.jpeg";
			case "9":
				return ".mp3,.wav";
			case "10":
				return ".mp4,.webm";
			case "11":
				return ".pdf,.doc,.docx,.txt";
			default:
				return (
					accept ||
					".mp3,.wav,.png,.jpg,.jpeg,.mp4,.webm,.pdf,.doc,.docx,.txt"
				);
		}
	};

	const handleFileChange = (e) => {
		const file = e.target.files[0];
		if (file) {
			onFileSend(null, { file, file_name: file.name }, selectedOption);
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
						navigate("/advanced");
						return;
					}
					inputRef.current?.click();
				}}
				className={`upload-btn ${disabled ? "disabled" : ""}`}
				disabled={disabled}
			>
				+
			</button>
			<input
				type="file"
				ref={inputRef}
				onChange={handleFileChange}
				style={{ display: "none" }}
				accept={getAcceptFormats()}
			/>
		</>
	);
};

export default FileUpload;
