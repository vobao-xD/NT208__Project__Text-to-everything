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
	<div className="body_title text-center space-y-4">
		<h1 className="text-4xl md:text-5xl font-bold text-white">{title}</h1>
		<h3 className="text-xl md:text-3xl text-gray-300">{slogan}</h3>
	</div>
);

// Danh sách chức năng
const FeatureList = ({ features }) => (
	<div className="mt-12">
		<h2 className="slogan text-2xl font-semibold text-center mb-6">Tôi có thể giúp gì được cho bạn?</h2>
		<ul>
			{features.map((feature, index) => (
				<li key={index}>
					<span>{feature.split(":")[0]}</span>
					<span className="emphasize">{feature.split(":")[1]} </span>
					<span>{feature.split(":")[2]}</span>
				</li>
			))}
		</ul>
		<h3 className="slogan text-2xl font-semibold text-center mb-6">Hàng loạt tính năng AI thông minh, sáng tạo và đột phá đang chờ bạn khám phá!</h3>
	</div>
);

const Home = () => {
	const navigate = useNavigate();

	const features = [
		"🎤:Text to Speech (Cơ bản):Biến văn bản thành giọng nói mượt mà, tự nhiên chỉ trong tích tắc.",
		"🎤:Text to Speech (Cá nhân hóa):Tạo ra giọng nói của riêng bạn — độc quyền, độc đáo, không ai giống ai!",
		"🖼️:Text to Image:Tưởng tượng ra gì, AI vẽ ngay cho bạn! Biến mô tả thành tác phẩm nghệ thuật sống động.",
		"📺:Text to Video:Chỉ cần ý tưởng — AI dựng video giúp bạn! Hoàn hảo cho sáng tạo nội dung, TikTok, YouTube…",
		"📁:File to Text:Chuyển đổi mọi loại file (âm thanh, hình ảnh, tài liệu) thành văn bản dễ xử lý, siêu nhanh.",
		"✨:Nâng Cấp Ảnh Chất Lượng Thấp:Ảnh mờ, ảnh cũ? Để AI biến nó thành hình ảnh sắc nét và rõ ràng như mới!",
		"🔥:Và đó mới chỉ là khởi đầu...",
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
					<h2 className="text-2xl font-bold">TRANG CHỦ</h2>
					<span className="text-gray-400">Khám phá AI</span>
				</div>
			</aside>

			{/* Main Content */}
			<main className="flex-1 p-6 md:p-12 content">
				<nav className="navbar content-item flex justify-end mb-8">
					<div className="navbar_btn flex gap-4">
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

				<section className="content_body mx-auto">
					<div>
						<ContentHeader
							title="CHÀO MỪNG BẠN ĐẾN VỚI AI FUTURE"
							slogan="🌐 Nơi Biến Văn Bản Thành Sáng Tạo Vượt Trội Với Trí Tuệ Nhân Tạo 🌐"
						/>
						<FeatureList features={features} />
					</div>
					<div className="text-center mt-12">
						<button
							onClick={handleGetStarted}
							className="start_btn px-8 py-4 bg-gradient-to-r from-cyan-300 to-blue-500 hover:from-blue-500 hover:to-cyan-300 text-white text-lg font-semibold rounded-xl shadow-lg transition duration-300"
							type="button"
							aria-label="Đăng ký ngay hôm nay"
						>
							Đăng ký ngay hôm nay
						</button>
					</div>
				</section>
			</main>
		</div>
	);
};

export default Home;
