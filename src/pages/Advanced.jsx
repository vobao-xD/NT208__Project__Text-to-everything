import React from 'react';
import "../Advanced.css";

const Advanced = () => {
  const handlePayment = async (plan) => {
    let amount;
    if (plan === "plus") {
      amount = 100000;
    } else if (plan === "pro") {
      amount = 200000;
    } else {
      alert("Gói không hợp lệ!");
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:8000/momo/create-payment?amount=${amount}`, {
        method: "POST",
        headers: {
          "Accept": "application/json",
        },
      });
      
      const data = await response.json();
      if (response.ok) {
        alert("Thanh toán thành công! Link: " + data.payUrl);
        window.location.href = data.payUrl;  
      } else {
        alert("Lỗi thanh toán: " + data.message);
      }
    } catch (error) {
      alert("Lỗi khi tạo đơn hàng!");
      console.error("Lỗi:", error);
    }
  };

  return (
    <>
      <h1>Nâng cấp gói của bạn</h1>
      <div className="container">
        <div className="plan free">
          <h2>Miễn Phí</h2>
          <p className="price">0 VND/Tháng</p>
          <p>Hỗ trợ người dùng mới, giới hạn 1 tháng</p>
          <ul>
            <li>✅ Text-to-Image cơ bản (giới hạn số lần/ngày)</li>
            <li>✅ Text-to-Speech (giọng cơ bản, giới hạn thời gian/ngày)</li>
            <li>✅ Speech-to-Text cơ bản (hỗ trợ tiếng Việt và tiếng Anh)</li>
            <li>✅ Lưu trữ 24 giờ</li>
            <li>✅ Truy cập chatbot AI (giới hạn số lần)</li>
          </ul>
          <button className="btn" style={{ marginTop: '100px' }}>Dùng thử miễn phí</button>
        </div>
        
        <div className="plan plus">
          <h2>Plus</h2>
          <p className="price">100.000 VND/Tháng</p>
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
            className="btn upgrade" 
            style={{marginTop:'48px'}}
            onClick={() => handlePayment('plus')}
          >
            Chuyển sang Plus
          </button>
        </div>
        
        <div className="plan pro">
          <h2>Pro</h2>
          <p className="price">200.000 VND/Tháng</p>
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
            className="btn upgrade" 
            style={{ marginTop: '91px' }} 
            onClick={() => handlePayment('pro')}
          >
            Chuyển sang Pro
          </button>
        </div>
      </div>
    </>
  );
};

export default Advanced;