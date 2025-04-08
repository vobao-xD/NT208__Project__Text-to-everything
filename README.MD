# Cấu trúc cây thư mục

Thư mục app chứa toàn bộ source code của backend

- api: chứa các endpoints, các loại endpoints khác nhau sẽ nằm trong các file khác nhau.
- core: chứa các logic chính của chương trình, cấu hình bảo mật như JWT, Oauth, cấu hình hệ thống, mã hóa,...
- db: chứa các thành phần liên quan đến cơ sở dữ liệu
  -- crud: chứa các hàm thao tác cơ sở dữ liệu
  -- database: kết nối với cơ sở dữ liệu
  -- model: chứa các bảng và cấu trúc DB cho SQAlchemy
  -- schema: định dạng các khung dữ liệu cho request và response
- services: chứa logic cho các api. Trong các endpoints chỉ cần gọi lại hàm được viết trong services. Mỗi loại service chứa ở các file riêng biệt

# Các ứng dụng cần cài

- Terminal
- WSL2
- Linux distro nên chọn: Ubuntu 24.04 LTS (ổn định nhất)
  --> Ai chưa biết cài thì lên mạng tìm hiểu hoặc có thể tham khảo ở đây nhe:
  https://www.youtube.com/watch?v=wOimgBphkE0

# Mẹo backend

- Lúc mới pull về, di chuyển tới thư mục tổng (NT208_Project), để cài các gói cần thiết ta chạy các lệnh sau
  sudo apt update
  sudo apt install python3
  sudo apt install python3-venv
  cd backend
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirement.txt

- Để chạy backend, ta di chuyển tới thư mục backend và nhập
  fastapi dev ./app/main.py

### => Nếu không hiểu thì hỏi mấy thằng làm backend :))
