import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";
import ChatBox from "@/components/ChatBox";
import InputBox from "@/components/InputBox";

const MainLayout = () => {
	return (
		<div className="full-container">
			<Sidebar />
			<div className="content">
				<Header />
				<ChatBox />
				<InputBox />
			</div>
		</div>
	);
};

export default MainLayout;
