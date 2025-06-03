import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Navigation button component
const NavButton = ({ onClick, label }) => (
  <button
    onClick={onClick}
    className="btn_login"
    type="button"
    aria-label={label}
  >
    {label}
  </button>
);

// Header component with animated title
const ContentHeader = ({ title, slogan }) => (
  <div className="body_title content-item">
    <h1 className="typing--animation">{title}</h1>
    <h3>{slogan}</h3>
  </div>
);

// Feature list component with icons
const FeatureList = ({ features }) => (
  <div className="body_description content-item">
    <h3 className="description_prompt">Tôi có thể giúp gì được cho bạn?</h3>
    <ul>
      {features.map((feature, index) => (
        <li key={index}>{feature}</li>
      ))}
    </ul>
  </div>
);

const Home = () => {
  const navigate = useNavigate();

  // Feature list
  const features = [
    'Text to Speech - Chuyển văn bản thành giọng nói',
    'Text to Image - Chuyển văn bản thành hình ảnh',
    'Text to Video - Chuyển văn bản thành video',
    'Create AI Avatar - Tạo avatar AI',
    'Improve Image Quality - Cải thiện chất lượng hình ảnh',
  ];

  // Handle "Get Started" button click
  const handleGetStarted = () => {
    if (localStorage.getItem('isLoggedIn') === 'true') {
      navigate('/generate');
    } else {
      toast.error('Bạn cần đăng nhập trước khi sử dụng tính năng này!', {
        position: 'top-right',
        autoClose: 2500,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        theme: 'colored',
      });
      navigate('/login');
    }
  };

  return (
    <div className="full-container">
      {/* Toast notification */}
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

      {/* Main content */}
      <main className="content">
        <nav className="navbar content-item">
          <div className="navbar_btn">
            <NavButton onClick={() => navigate('/signup')} label="Sign Up" />
            <NavButton onClick={() => navigate('/login')} label="Sign In" />
          </div>
        </nav>

        <section className="content_body">
          <ContentHeader
            title="CHÀO MỪNG BẠN ĐẾN VỚI AI FUTURE"
            slogan="Khám phá sức mạnh của trí tuệ nhân tạo"
          />
          <FeatureList features={features} />
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