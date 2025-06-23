import { ToastContainer, Slide } from "react-toastify";
import { BadgeCheck, CircleAlert, Info, TriangleAlert } from "lucide-react";
import "react-toastify/dist/ReactToastify.css";

const ToastProvider = ({ children }) => {
	return (
		<>
			{children}
			<ToastContainer
				position="top-right"
				autoClose={3000}
				hideProgressBar
				closeOnClick
				pauseOnHover
				draggable
				theme="dark"
				transition={Slide}
				stacked
				icon={({ type }) => {
					switch (type) {
						case "info":
							return <Info className="stroke-indigo-400" />;
						case "error":
							return <CircleAlert className="stroke-red-500" />;
						case "success":
							return <BadgeCheck className="stroke-green-500" />;
						case "warning":
							return (
								<TriangleAlert className="stroke-yellow-500" />
							);
						default:
							return null;
					}
				}}
			/>
		</>
	);
};

export default ToastProvider;
