import { useContext } from "react";
import { ChatContext } from "@/context/ChatContext";
import { useNavigate } from "react-router-dom";

const Header = () => {
	const { email, selectedOption, isLoading } = useContext(ChatContext);
	const navigate = useNavigate();

	return (
		<div className="header_content content-item">
			<div className="fixed-button-container">
				<button
					className={`rainbow-button fixed-button-advanced ${
						isLoading ? "disabled" : ""
					}`}
					onClick={() => navigate("/advanced")}
					disabled={isLoading}
				>
					Advanced
				</button>
			</div>
			<div className="user-info">
				<i className="fa-solid fa-circle-user fa-2x avatar"></i>
				<span className="username">{email || "User"}</span>
			</div>
			<div className="mode-info">
				Chế độ:{" "}
				{selectedOption === "0" ? "Auto Analyze" : selectedOption}
			</div>
		</div>
	);
};

export default Header;
