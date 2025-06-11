import React, { useRef } from "react";

const FileUpload = ({
	onFileSend,
	accept = ".mp3,.wav,.png,.jpg,.jpeg,.mp4,.webm,.pdf,.doc,.docx,.txt",
	disabled = false,
	selectedOption,
}) => {
	const inputRef = useRef();

	const handleFileChange = async (e) => {
		const file = e.target.files[0];
		if (file) {
			const data = {
				file,
				file_name: file.name,
				option: selectedOption,
			};
			onFileSend(null, data, selectedOption);
		}
	};

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
				return accept;
		}
	};

	return (
		<>
			<button
				onClick={() => {
					const role = localStorage.getItem("role");
					if (role === "free") {
						alert(
							"Tài khoản miễn phí không được phép upload. Vui lòng nâng cấp lên Plus hoặc Pro để sử dụng tính năng này!"
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
