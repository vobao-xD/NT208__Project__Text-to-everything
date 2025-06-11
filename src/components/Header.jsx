import React from "react";
import { useNavigate } from "react-router-dom";

const Header = ({ selectedOption }) => {
	const navigate = useNavigate();
	const username = localStorage.getItem("username") || "User"; // Lấy tên người dùng từ localStorage

	// Hiển thị tên định dạng hiện tại dựa trên selectedOption
	const getFormatLabel = () => {
		switch (selectedOption) {
			case "1":
				return "Audio";
			case "2":
				return "Image";
			case "3":
				return "Video";
			case "4":
				return "File";
			default:
				return "Text";
		}
	};

	return (
		<div className="header_content">
			<div className="fixed-button-container">
				<button
					className="fixed-button"
					onClick={() => navigate("/advanced")}
				>
					Advanced
				</button>
			</div>
			<div className="user-info">
				<i className="fa-solid fa-circle-user fa-2x avatar"></i>
				<span className="username">{username}</span>
				<span className="format-label">Mode: {getFormatLabel()}</span>
			</div>
		</div>
	);
};

export default Header;
