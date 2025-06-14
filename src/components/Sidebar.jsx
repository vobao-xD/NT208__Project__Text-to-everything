import { useContext, useState } from "react";
import { ChatContext } from "@/context/ChatContext";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

const Sidebar = () => {
	const navigate = useNavigate();
	const {
		isLoading,
		role,
		selectedOption,
		setSelectedOption,
		messages,
		conversations,
		currentConversationId,
		loadConversation,
		createConversation,
		deleteConversation,
	} = useContext(ChatContext);
	const [isManualMode, setIsManualMode] = useState(false);
	const [showFunctionDropdown, setShowFunctionDropdown] = useState(false);

	const handleModeChange = (e) => {
		const newMode = e.target.value;
		if (newMode === "1.1" && role !== "pro") {
			toast.error("Chỉ tài khoản Pro mới được phép sử dụng chế độ 1.1!");
			navigate("/advanced");
			return;
		}
		setSelectedOption(newMode);
	};

	const handleManualModeToggle = () => {
		const newMode = !isManualMode;
		setIsManualMode(newMode);
		setShowFunctionDropdown(newMode);
		if (!newMode) setSelectedOption("0");
	};

	const handleOptionChange = (e) => {
		const newValue = e.target.value;
		if (newValue === "0") {
			setIsManualSelection(false);
		} else {
			setIsManualSelection(true);
		}
		setSelectedOption(newValue);
	};

	return (
		<div className="sidebar">
			<button className="back-button" onClick={() => navigate("/")}>
				<i className="fa fa-home"></i>
			</button>
			<div className="sidebar_title">
				<h2>Sidebar</h2>
			</div>
			<div className="mode-selection">
				<select
					className={`options ${
						isLoading ? "disabled" : ""
					} focus:border-blue-600`}
					value={selectedOption}
					onChange={handleModeChange}
					disabled={isLoading}
				>
					<option value="1">API-Model 1</option>
					<option value="1.1" disabled={role !== "pro"}>
						API-Model 1.1
					</option>
				</select>
			</div>
			<div className="manual-mode-toggle" style={{ margin: "10px 0" }}>
				<button
					className={`toggle-button ${isManualMode ? "active" : ""}`}
					onClick={handleManualModeToggle}
					style={{
						padding: "8px 15px",
						borderRadius: "5px",
						border: "none",
						background: isManualMode
							? "linear-gradient(135deg, #3999ff, #50e2ff)"
							: "#2a2a2a",
						color: isManualMode ? "black" : "white",
						cursor: "pointer",
						transition: "all 0.3s ease",
						display: "flex",
						alignItems: "center",
						gap: "8px",
					}}
				>
					<i
						className={`fa ${
							isManualMode ? "fa-check-circle" : "fa-cog"
						}`}
					></i>
					{isManualMode ? "Chế độ thủ công" : "Chế độ tự động"}
				</button>
			</div>
			{showFunctionDropdown && (
				<div className="choices">
					<select
						className={`options ${
							isLoading ? "disabled" : ""
						} focus:border-blue-600`}
						value={selectedOption}
						onChange={handleOptionChange}
						disabled={isLoading}
					>
						<option value="0">Auto Analyze</option>
						<option value="1">
							Text to Speech (Default Voice)
						</option>
						<option value="2">Text to Image</option>
						<option value="3">Text to Video</option>
						<option value="4">Text to Speech (Custom Voice)</option>
						<option value="5">Improve Image Quality</option>
						<option value="6">AI Chatbox</option>
						<option value="7">Answer Question</option>
						<option value="8">Generate code</option>
						<option value="9">Speech to Text</option>
						<option value="10">Video to Text</option>
						<option value="11">File to Text</option>
					</select>
				</div>
			)}
			<div className="new-chat_btn">
				<button
					className={`generate_btn ${isLoading ? "disabled" : ""}`}
					onClick={createConversation}
					disabled={isLoading}
				>
					+ Cuộc trò chuyện mới
				</button>
			</div>
			<div className="history">
				<ul
					className="chat-list"
					style={{
						listStyle: "none",
						padding: 0,
						cursor: "pointer",
					}}
				>
					{conversations.map((conversation) => (
						<li
							key={conversation.id}
							className={`chat-item ${
								currentConversationId === conversation.id
									? "active"
									: ""
							}`}
							style={{
								padding: "10px 15px",
								margin: "5px 0",
								borderRadius: "8px",
								backgroundColor:
									currentConversationId === conversation.id
										? "#2a2a2a"
										: "transparent",
								border:
									currentConversationId === conversation.id
										? "1px solid #3999ff"
										: "1px solid transparent",
								transition: "all 0.3s ease",
								display: "flex",
								alignItems: "center",
								justifyContent: "space-between",
								"&:hover": {
									backgroundColor: "#2a2a2a",
									transform: "translateX(5px)",
								},
							}}
						>
							<span
								onClick={() =>
									loadConversation(conversation.id)
								}
								style={{
									color:
										currentConversationId ===
										conversation.id
											? "#3999ff"
											: "#fff",
									fontWeight:
										currentConversationId ===
										conversation.id
											? "bold"
											: "normal",
									transition: "all 0.3s ease",
								}}
							>
								{conversation.title}
							</span>
							<button
								onClick={(e) => {
									e.stopPropagation();
									deleteConversation(conversation.id);
								}}
								style={{
									background: "transparent",
									color: "#ff4444",
									border: "none",
									padding: "2px 6px",
									borderRadius: "5px",
									cursor: "pointer",
									marginLeft: "10px",
									opacity:
										currentConversationId ===
										conversation.id
											? 1
											: 0.5,
									transition: "all 0.3s ease",
									"&:hover": {
										opacity: 1,
										backgroundColor:
											"rgba(255, 68, 68, 0.1)",
									},
								}}
							>
								🞬
							</button>
						</li>
					))}
				</ul>
			</div>
		</div>
	);
};

export default Sidebar;
