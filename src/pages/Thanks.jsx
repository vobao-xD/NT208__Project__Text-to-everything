import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Thanks = () => {
    const navigate = useNavigate();

    // Tự động chuyển hướng sau 5 giây
    useEffect(() => {
        const timer = setTimeout(() => {
            navigate('/generate');
        }, 5000);

        return () => clearTimeout(timer); // Xóa timer khi unmount
    }, [navigate]);

    return (
        <div className="thanks-container">
            <div className="thanks-box">
                <h2 className="thanks-title">Cảm ơn bạn!</h2>
                <p className="thanks-message">
                    Bạn đã thanh toán thành công. Chúc bạn sử dụng thành công!
                </p>
                <a
                    href="#"
                    onClick={(e) => {
                        e.preventDefault();
                        navigate('/generate');
                    }}
                    className="login-redirect"
                >
                    Sử dụng ngay!
                </a>
                <p className="thanks-note">
                    Bạn sẽ được chuyển hướng tự động sau 5 giây...
                </p>
            </div>
        </div>
    );
};

export default Thanks;
