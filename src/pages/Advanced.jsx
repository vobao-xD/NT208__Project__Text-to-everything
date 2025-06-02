import React, { useEffect, useState } from 'react';
import "../Advanced.css";
import { useNavigate } from 'react-router-dom';

import {toast, ToastContainer,Slide} from 'react-toastify';
import { BadgeCheck, CircleAlert, Info, TriangleAlert } from 'lucide-react';


const Advanced = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('monthly'); // 'monthly' hoặc 'yearly'

  useEffect(() => {
    async function fetchUserData() {
      const email = localStorage.getItem("email");
      if (!email) {
        // alert("No email found in localStorage");
        toast.error("No email found in localStorage",{
            closeButton: true,
            className: 'p-0 w-[400px] border border-red-600/40 backdrop-blur-lg',
            ariaLabel: 'Warn',
        })
        return;
      }
      
      const response = await fetch(`http://localhost:8000/user-subscription?email=${email}`, {
        method: "GET",
        headers: {
          "Accept": "application/json",
        },
      });

      const data = await response.json();
      // Giả sử API trả về: { role: "plus", billingCycle: "monthly" }
      localStorage.setItem("role", data.role);
      localStorage.setItem("billingCycle", data.billingCycle || "monthly");
    }
    fetchUserData();
  }, [activeTab]); // Re-fetch khi đổi tab

  const getPricing = () => {
    if (activeTab === 'monthly') {
      return {
        plus: { amount: 100000, display: '100.000 VND/Tháng' },
        pro: { amount: 200000, display: '200.000 VND/Tháng' }
      };
    } else {
      return {
        plus: { amount: 1000000, display: '1.000.000 VND/Năm', original: '1.200.000 VND', discount: 'Tiết kiệm 200.000 VND' },
        pro: { amount: 2000000, display: '2.000.000 VND/Năm', original: '2.400.000 VND', discount: 'Tiết kiệm 400.000 VND' }
      };
    }
  };

  const getButtonStatus = (plan) => {
    const currentRole = localStorage.getItem("role");
    const currentBillingCycle = localStorage.getItem("billingCycle"); // Lưu chu kỳ thanh toán hiện tại
    
    if (plan === 'free') {
      if (currentRole === "free") {
        return { disabled: true, text: 'Đã sử dụng' };
      }
      if (currentRole === "plus" || currentRole === "pro") {
        return { disabled: true, text: 'Đã nâng cấp' };
      }
      return { disabled: false, text: 'Dùng thử miễn phí' };
    }
    
    if (plan === 'plus') {
      if (currentRole === "pro") {
        return { disabled: true, text: 'Đã sử dụng gói cao hơn' };
      }
      if (currentRole === "plus") {
        if (currentBillingCycle === activeTab) {
          return { disabled: true, text: 'Đã sử dụng' };
        } else {
          // Đã dùng Plus nhưng chu kỳ khác -> cho phép chuyển đổi
          if(activeTab === 'monthly' && currentBillingCycle === 'yearly') {
            return { 
              disabled: true, 
              text: 'Đã sử dụng gói cao cấp hơn',
              isUpgrade: true
            };
          }
          return { 
            disabled: false, 
            text: activeTab === 'yearly' ? 'Chuyển sang năm' : 'Chuyển sang tháng',
            isUpgrade: true
          };
        }
      }
      return { disabled: false, text: 'Chuyển sang Plus' };
    }
    
    if (plan === 'pro') {
      if (currentRole === "pro") {
        if (currentBillingCycle === activeTab) {
          return { disabled: true, text: 'Đã sử dụng' };
        } else {
          if(activeTab === 'monthly' && currentBillingCycle === 'yearly') {
            return { 
              disabled: true, 
              text: 'Đã sử dụng gói cao cấp hơn',
              isUpgrade: true
            };
          }
          return { 
            disabled: false, 
            text: activeTab === 'yearly' ? 'Chuyển sang năm' : 'Chuyển sang tháng',
            isUpgrade: true
          };
        }
      }
      if (currentRole === "plus") {
        return { disabled: false, text: 'Nâng cấp lên Pro' };
      }
      return { disabled: false, text: 'Chuyển sang Pro' };
    }
  };

  const handlePayment = async (plan) => {
    const pricing = getPricing();
    const currentRole = localStorage.getItem("role");
    const currentBillingCycle = localStorage.getItem("billingCycle");
    let amount;
    
    if (plan === "plus") {
      amount = pricing.plus.amount;
      if (currentRole === "pro" && currentBillingCycle === activeTab) {
        // alert("Bạn đã sử dụng gói Pro với chu kỳ này");
        toast.warning("Bạn đã sử dụng gói Pro với chu kỳ này",{
            closeButton: true,
            className: 'p-0 w-[400px] border border-yellow-600/40 backdrop-blur-lg',
            ariaLabel: 'Warn',
        })
        return;
      }
    } else if (plan === "pro") {
      amount = pricing.pro.amount;
      // Không cần check nếu đang chuyển từ Plus sang Pro
    } else {
      if (currentRole === "pro" || currentRole === "plus") {
        // alert("Bạn đã có gói cao hơn");
        toast.warning("Bạn đã có gói cao hơn",{
            closeButton: true,
            className: 'p-0 w-[400px] border border-yellow-600/40 backdrop-blur-lg',
            ariaLabel: 'Warn',
        })
        return;
      }
      navigate('/generate');
      return;
    }
    
    try {
      const email = localStorage.getItem("email");
      const response = await fetch(`http://localhost:8000/momo/create-payment`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json",
        },
        body: JSON.stringify({
          amount: amount,
          email: email, 
          plan: plan,
          billingCycle: activeTab,
          currentRole: currentRole,
          currentBillingCycle: currentBillingCycle
        })
      });
      
      const data = await response.json();
      if (response.ok) {
        // alert("Thanh toán thành công! Link: " + data.payUrl);
        toast.info("Thanh toán thành công!",{
            closeButton: true,
            className: 'p-0 w-[400px] border border-green-600/40 backdrop-blur-lg',
            ariaLabel: 'Info',
        })
        window.location.href = data.payUrl;  
      } else {
        // alert("Lỗi thanh toán: " + data.message);
        toast.error("Lỗi thanh toán: " + data.message,{
            closeButton: true,
            className: 'p-0 w-[400px] border border-red-600/40 backdrop-blur-lg',
            ariaLabel: 'Info',
        })
      }
    } catch (error) {
      // alert("Lỗi khi tạo đơn hàng!");
      toast.error("Lỗi khi tạo đơn hàng!",{
            closeButton: true,
            className: 'p-0 w-[400px] border border-red-600/40 backdrop-blur-lg',
            ariaLabel: 'Info',
        })
      console.error("Lỗi:", error);
    }
  };

  const pricing = getPricing();

  return (
    <>
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={true}
        closeOnClick
        pauseOnHover
        draggable
        theme="light"
        transition={Slide}
        stacked
        icon={({ type, theme }) => {
        // theme is not used in this example but you could
        switch (type) {
            case 'info':
            return <Info className="stroke-indigo-400" />;
            case 'error':
            return <CircleAlert className="stroke-red-500" />;
            case 'success':
            return <BadgeCheck className="stroke-green-500" />;
            case 'warning':
            return <TriangleAlert className="stroke-yellow-500" />;
            default:
            return null;
        }
        }}
          />
      <h1>Nâng cấp gói của bạn</h1>
      
      {/* Tab Navigation */}
      <div className="billing-tabs" style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        marginBottom: '30px',
        borderBottom: '1px solid #e0e0e0'
      }}>
        <button 
          className={`tab-button ${activeTab === 'monthly' ? 'active' : ''}`}
          onClick={() => setActiveTab('monthly')}
          style={{
            padding: '12px 24px',
            border: 'none',
            background: activeTab === 'monthly' ? '#007bff' : 'transparent',
            color: activeTab === 'monthly' ? 'white' : '#666',
            cursor: 'pointer',
            borderRadius: '8px 8px 0 0',
            fontSize: '16px',
            fontWeight: '500',
            marginRight: '4px'
          }}
        >
          Thanh toán theo tháng
        </button>
        <button 
          className={`tab-button ${activeTab === 'yearly' ? 'active' : ''}`}
          onClick={() => setActiveTab('yearly')}
          style={{
            padding: '12px 24px',
            border: 'none',
            background: activeTab === 'yearly' ? '#007bff' : 'transparent',
            color: activeTab === 'yearly' ? 'white' : '#666',
            cursor: 'pointer',
            borderRadius: '8px 8px 0 0',
            fontSize: '16px',
            fontWeight: '500',
            position: 'relative'
          }}
        >
          Thanh toán theo năm
          <span style={{
            position: 'absolute',
            top: '-8px',
            right: '-8px',
            background: '#ff4757',
            color: 'white',
            fontSize: '10px',
            padding: '2px 6px',
            borderRadius: '10px'
          }}>
            SAVE
          </span>
        </button>
      </div>

      <div className="container">
        <div className="plan free">
          <h2>Miễn Phí</h2>
          <p className="price">0 VND</p>
          <p>Hỗ trợ người dùng mới, giới hạn 1 tháng</p>
          <ul>
            <li>✅ Text-to-Image cơ bản (giới hạn số lần/ngày)</li>
            <li>✅ Text-to-Speech (giọng cơ bản, giới hạn thời gian/ngày)</li>
            <li>✅ Speech-to-Text cơ bản (hỗ trợ tiếng Việt và tiếng Anh)</li>
            <li>✅ Lưu trữ 24 giờ</li>
            <li>✅ Truy cập chatbot AI (giới hạn số lần)</li>
          </ul>
          <button 
            id="free-button"
            className={`btn ${getButtonStatus('free').disabled ? 'disabled-btn' : ''}`}
            style={{ 
              marginTop: '100px',
              cursor: getButtonStatus('free').disabled ? 'not-allowed' : 'pointer',
              backgroundColor: getButtonStatus('free').disabled ? 'white' : '',
              color: getButtonStatus('free').disabled ? 'black' : ''
            }}
            disabled={getButtonStatus('free').disabled}
            onClick={() => handlePayment('free')}
          >
            {getButtonStatus('free').text}
          </button>
        </div>
        
        <div className="plan plus">
          <h2>Plus</h2>
          <div className="price-container">
            <p className="price">{pricing.plus.display}</p>
            {activeTab === 'yearly' && pricing.plus.original && (
              <>
                <p className="original-price" style={{ 
                  textDecoration: 'line-through', 
                  color: '#999', 
                  fontSize: '14px',
                  margin: '0'
                }}>
                  {pricing.plus.original}
                </p>
                <p className="discount" style={{ 
                  color: '#28a745', 
                  fontSize: '12px',
                  fontWeight: 'bold',
                  margin: '4px 0'
                }}>
                  {pricing.plus.discount}
                </p>
              </>
            )}
          </div>
          <p>Nâng cao hiệu suất, không giới hạn lượt truy cập</p>
          <ul>
            <li>🔥 Tất cả quyền lợi của gói Miễn phí</li>
            <li>✅ Text-to-Image nâng cao (AI chất lượng cao, giảm thời gian chờ)</li>
            <li>✅ Text-to-Speech (giọng AI tự nhiên, nhiều ngôn ngữ)</li>
            <li>✅ Speech-to-Text nâng cao (chính xác hơn, hỗ trợ đa giọng)</li>
            <li>✅ Lưu trữ nội dung trong 7 ngày</li>
            <li>✅ Không có quảng cáo</li>
          </ul>
          <button
            id="plus-button"
            className={`btn upgrade ${getButtonStatus('plus').disabled ? 'disabled-btn' : ''}`}
            style={{ 
              marginTop: activeTab === 'yearly' ? '20px' : '48px',
              cursor: getButtonStatus('plus').disabled ? 'not-allowed' : 'pointer',
              backgroundColor: getButtonStatus('plus').disabled ? 'white' : getButtonStatus('plus').isUpgrade ? '#28a745' : '',
              color: getButtonStatus('plus').disabled ? 'black' : ''
            }}
            disabled={getButtonStatus('plus').disabled}
            onClick={() => handlePayment('plus')}
          >
            {getButtonStatus('plus').text}
          </button>
        </div>
        
        <div className="plan pro">
          <h2>Pro</h2>
          <div className="price-container">
            <p className="price">{pricing.pro.display}</p>
            {activeTab === 'yearly' && pricing.pro.original && (
              <>
                <p className="original-price" style={{ 
                  textDecoration: 'line-through', 
                  color: '#999', 
                  fontSize: '14px',
                  margin: '0'
                }}>
                  {pricing.pro.original}
                </p>
                <p className="discount" style={{ 
                  color: '#28a745', 
                  fontSize: '12px',
                  fontWeight: 'bold',
                  margin: '4px 0'
                }}>
                  {pricing.pro.discount}
                </p>
              </>
            )}
          </div>
          <p>Truy cập nhanh hơn, lưu trữ lớn hơn, quyền sử dụng cao nhất</p>
          <ul>
            <li>🔥 Tất cả quyền lợi của gói Plus</li>
            <li>✅ Text-to-Video (AI tạo video từ văn bản, nhân vật ảo)</li>
            <li>✅ AI Character Animation (tạo nhân vật động theo giọng nói)</li>
            <li>✅ Lưu trữ không giới hạn</li>
            <li>✅ Tăng tốc xử lý (ưu tiên hàng đợi)</li>
            <li>✅ API riêng để tích hợp dự án</li>
          </ul>
          <button 
            id="pro-button"
            className={`btn upgrade ${getButtonStatus('pro').disabled ? 'disabled-btn' : ''}`}
            style={{ 
              marginTop: activeTab === 'yearly' ? '63px' : '91px',
              cursor: getButtonStatus('pro').disabled ? 'not-allowed' : 'pointer',
              backgroundColor: getButtonStatus('pro').disabled ? 'white' : getButtonStatus('pro').isUpgrade ? '#28a745' : '',
              color: getButtonStatus('pro').disabled ? 'black' : ''
            }}
            disabled={getButtonStatus('pro').disabled}
            onClick={() => handlePayment('pro')}
          >
            {getButtonStatus('pro').text}
          </button>
        </div>
      </div>
    </>
  );
};

export default Advanced;