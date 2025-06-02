// FileUpload.jsx
import React, { useRef } from 'react';

const FileUpload = ({ onFileSend, accept = ".mp3,.wav,.mp4", disabled = false }) => {
  const inputRef = useRef();

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      onFileSend(file); // Gửi file về component cha xử lý
    }
  };

  return (
    <>
      <button 
        onClick={() => {
          const role = localStorage.getItem("role");
          if (role === "free") {
            alert("Tài khoản miễn phí không được phép upload. Vui lòng nâng cấp lên Plus hoặc Pro để sử dụng tính năng này!");
            return;
          }
          inputRef.current.click();
        }}
        className={`upload-btn ${disabled ? 'disabled' : ''}`}
        disabled={disabled}
      >
        +
      </button>
      <input
        type="file"
        accept={accept}
        style={{ display: "none" }}
        ref={inputRef}
        onChange={handleFileChange}
        disabled={disabled}
      />
    </>
  );
};

export default FileUpload;
