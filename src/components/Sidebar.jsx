import { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ChatContext } from "@/context/ChatContext";
import { toast } from "react-toastify";

const Sidebar = () => {
	const navigate = useNavigate();
	const {
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
		setSelectedOption(e.target.value);
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
					className="options"
					value={selectedOption}
					onChange={handleModeChange}
					disabled={messages.length > 0}
				>
					<option value="1">API-Model 1</option>
					<option value="1.1">API-Model 1.1</option>
				</select>
			</div>
			<div className="manual-mode-toggle">
				<button
					className={`toggle-button ${isManualMode ? "active" : ""}`}
					onClick={handleManualModeToggle}
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
						className="options"
						value={selectedOption}
						onChange={handleOptionChange}
					>
						<option value="0">Auto Analyze</option>
						<option value="1">Text to Speech</option>
						<option value="2">Text to Image</option>
						<option value="3">Text to Video</option>
						<option value="4">Text to Text</option>
						<option value="5">Improve Image Quality</option>
						<option value="6">AI Chatbot</option>
						<option value="7">Answer Question</option>
						<option value="8">Generate Code</option>
						<option value="9">Speech to Text</option>
						<option value="10">Video to Text</option>
						<option value="11">File to Text</option>
					</select>
				</div>
			)}
			<div className="new-chat_btn">
				<button className="generate_btn" onClick={createConversation}>
					+ Cuộc trò chuyện mới
				</button>
			</div>
			<div className="history">
				<ul className="chat-list">
					{conversations.map((conversation) => (
						<li
							key={conversation.id}
							className={`chat-item ${
								currentConversationId === conversation.id
									? "active"
									: ""
							}`}
						>
							<span
								onClick={() =>
									loadConversation(conversation.id)
								}
							>
								{conversation.title}
							</span>
							<button
								onClick={() =>
									deleteConversation(conversation.id)
								}
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
