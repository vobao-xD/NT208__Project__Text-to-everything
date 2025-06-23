import { ChatProvider } from "@/context/ChatContext";
import MainLayout from "@/layouts/MainLayout";
import ToastProvider from "@/components/ToastProvider";

const Generate = () => {
	return (
		<ChatProvider>
			<ToastProvider>
				<MainLayout />
			</ToastProvider>
		</ChatProvider>
	);
};

export default Generate;
