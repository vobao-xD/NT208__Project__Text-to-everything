import React from "react";
import { useNavigate } from "react-router-dom";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// Nút điều hướng đơn giản
const NavButton = ({ onClick, label }) => (
	<button
		className="btn_login"
		onClick={onClick}
		type="button"
		aria-label={label}
	>
		{label}
	</button>
);

const ContentHeader = ({ title, slogan }) => (
	<div className="body_title content-item">
		<h1 style={{ minWidth: "600px", color: "white" }}>{title}</h1>
		<h3>{slogan}</h3>
	</div>
);

// Danh sách chức năng
const FeatureList = ({ features }) => (
	<div className="body_description content-item">
		<h2 className="description_prompt">Tôi có thể giúp gì được cho bạn?</h2>
		<ul>
			{features.map((feature, index) => (
				<li key={index}>{feature}</li>
			))}
		</ul>
	</div>
);

const Home = () => {
	const navigate = useNavigate();

	const features = [
		"🎤 Text to Speech (Default) - Chuyển văn bản thành giọng nói mặc định 🎤",
		"🎤 Text to Speech (Advanced) - Chuyển văn bản thành giọng nói riêng của bạn 🎤",
		"🖼️ Text to Image - Chuyển văn bản thành hình ảnh 🖼️",
		"📺 Text to Video - Chuyển văn bản thành video 📺",
		"📁 File to Text - Chuyển đổi các dạng dữ liệu thành văn bản 📁",
		"✨ Improve Image Quality - Cải thiện chất lượng hình ảnh ✨",
		"🔥 Và còn vô vàn tính năng hay ho đang chờ bạn khám phá đó! 🔥",
	];

	const handleGetStarted = () => {
		const isLoggedIn = localStorage.getItem("isLoggedIn") === "true";

		if (isLoggedIn) {
			navigate("/generate");
		} else {
			toast.error("Bạn cần đăng nhập trước khi sử dụng tính năng này!", {
				position: "top-right",
				autoClose: 2500,
				hideProgressBar: false,
				closeOnClick: true,
				pauseOnHover: true,
				draggable: true,
				theme: "colored",
			});
		}
	};

	return (
		<div className="full-container">
			<ToastContainer
				position="top-right"
				autoClose={2500}
				hideProgressBar={false}
				closeOnClick
				pauseOnHover
				draggable
				stacked
				theme="dark"
			/>

			{/* Sidebar */}
			<aside className="sidebar">
				<div className="sidebar_text">
					<h2>TRANG CHỦ</h2>
					<span>Khám phá AI</span>
				</div>
			</aside>

			{/* Main Content */}
			<main className="content">
				<nav className="navbar content-item">
					<div className="navbar_btn">
						<NavButton
							onClick={() => navigate("/signup")}
							label="Sign Up"
						/>
						<NavButton
							onClick={() => navigate("/login")}
							label="Sign In"
						/>
					</div>
				</nav>

				<section className="content_body">
					<div>
						<ContentHeader
							title="🌐 CHÀO MỪNG BẠN ĐẾN VỚI AI FUTURE 🌐"
							slogan="Khám phá sức mạnh của trí tuệ nhân tạo"
						/>
						<FeatureList features={features} />
					</div>
					<div>
						<button
							onClick={handleGetStarted}
							className="start_btn"
							type="button"
							aria-label="Bắt đầu nào"
						>
							BẮT ĐẦU NÀO
						</button>
					</div>
				</section>
			</main>
		</div>
	);
};

export default Home;
