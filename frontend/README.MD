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
