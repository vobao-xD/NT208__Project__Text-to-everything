# 🧠 Text to Everything

**Text to Everything** là một nền tảng AI đa năng, được thiết kế để trao quyền sáng tạo cho người dùng bằng cách chuyển đổi văn bản hoặc giọng nói thành nhiều định dạng nội dung phong phú. Từ hình ảnh nghệ thuật, video hoạt hình, bản thu âm giọng nói AI chuyên nghiệp, cho đến kịch bản sáng tạo và nhân vật ảo, tất cả đều được tạo ra một cách dễ dàng. Dự án được phát triển bằng Python và FastAPI, sử dụng PostgreSQL làm cơ sở dữ liệu, tích hợp các mô hình AI tiên tiến, và hỗ trợ giao diện thân thiện với ưu tiên tối ưu hóa cho tiếng Việt.

---

## 📌 Tổng quan

-   **Đồ án môn học**: Lập trình Ứng dụng Web - **NT208.P23.ANTT**
-   **Giáo viên hướng dẫn**: Trần Tuấn Dũng
-   **Ngày cập nhật**: 06/07/2025

---

## 👨‍💻 Thành viên nhóm

| Tên thành viên        | MSSV     |
| --------------------- | -------- |
| Võ Quốc Bảo           | 23520146 |
| Hà Sơn Bin            | 23520149 |
| Nguyễn Đoàn Gia Khánh | 23520720 |
| Tạ Ngọc Ân            | 23520030 |
| Nguyễn Thái Học       | 23520549 |

---

## 🗂 Mục lục

-   [🔍 Giới thiệu](#-giới-thiệu)
-   [🚀 Các tính năng chính](#-các-tính-năng-chính)
-   [🧑‍💻 Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
-   [🛠 Công nghệ sử dụng](#-công-nghệ-sử-dụng)
-   [📦 Cài đặt và chạy dự án](#-cài-đặt-và-chạy-dự-án)
    -   [Điều kiện tiên quyết](#điều-kiện-tiên-quyết)
    -   [Các bước cài đặt](#các-bước-cài-đặt)
    -   [Cấu hình môi trường](#cấu-hình-môi-trường)
    -   [Khởi chạy ứng dụng](#khởi-chạy-ứng-dụng)
-   [🧪 Tài liệu API](#-tài-liệu-api)
-   [👤 Tài khoản và phân quyền](#-tài-khoản-và-phân-quyền)
-   [📊 Demo và minh họa](#-demo-và-minh-họa)
-   [💡 Đóng góp](#-đóng-góp)
-   [📄 Giấy phép (License)](#-giấy-phép-license)
-   [📞 Liên hệ](#-liên-hệ)

---

## 🔍 Giới thiệu

**Text to Everything** ra đời với tầm nhìn tiên phong trong việc cách mạng hóa sáng tạo nội dung thông qua trí tuệ nhân tạo (AI), mang đến một giải pháp toàn diện phục vụ mọi đối tượng - từ người dùng phổ thông mong muốn tạo ra các sản phẩm độc đáo cho cá nhân, đến các nhà sáng tạo nội dung chuyên nghiệp, nhà tiếp thị, và nhà phát triển tìm kiếm công cụ mạnh mẽ để hiện thực hóa ý tưởng.

Trong kỷ nguyên số hóa, nhu cầu về nội dung trực quan, sống động và chất lượng cao ngày càng trở nên cấp thiết. Tuy nhiên, không phải ai cũng sở hữu kỹ năng thiết kế, thời gian hay nguồn lực để sản xuất hình ảnh, video, hoặc âm thanh ấn tượng. **Text to Everything** khắc phục rào cản này bằng cách cung cấp một nền tảng tích hợp, nơi người dùng chỉ cần cung cấp văn bản hoặc giọng nói, hệ thống AI tiên tiến sẽ tự động xử lý và tạo ra các sản phẩm đa dạng.

Với cam kết không ngừng cải tiến và tích hợp các mô hình AI mới nhất, **Text to Everything** hướng đến việc trở thành công cụ sáng tạo toàn diện, đáp ứng mọi nhu cầu đa dạng của người dùng trên toàn cầu.

---

## 🚀 Các tính năng chính

Dưới đây là những tính năng nổi bật, mang tính đột phá của **Text to Everything**, giúp tối ưu hóa trải nghiệm sáng tạo cho người dùng:

| Tính năng                | Mô tả chi tiết                                                                                                                                                             |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🗣️ Text-to-Speech (TTS)  | Biến văn bản thành giọng nói tự nhiên, linh hoạt với nhiều ngôn ngữ, đặc biệt tối ưu hóa cho tiếng Việt với ngữ điệu phong phú.                                            |
| 🗣️ Voice Cloning         | Sao chép giọng nói độc đáo của người dùng thông qua mô hình Vi-XTTS, tạo TTS tùy chỉnh với chất lượng chuyên nghiệp.                                                       |
| 🖼️ Text-to-Image         | Chuyển đổi mô tả văn bản thành hình ảnh nghệ thuật, chân thực hoặc trừu tượng bằng mô hình khuếch tán (Diffusion Models), hỗ trợ tùy chỉnh phong cách và độ phân giải cao. |
| 📽️ Text-to-Video         | Tạo video ngắn từ kịch bản văn bản với các cảnh động đơn giản, tích hợp âm thanh AI tự nhiên và hiệu ứng sinh động.                                                        |
| 📄 Text-to-Code          | Tự động sinh mã nguồn chất lượng (Python, C++, C, v.v.) từ yêu cầu văn bản, phù hợp cho lập trình viên và người mới bắt đầu.                                               |
| ✍️ Bot sáng tạo nội dung | Hỗ trợ tạo nội dung sáng tạo như truyện ngắn, kịch bản, slogan, bài đăng mạng xã hội từ gợi ý, phù hợp cho mọi nhu cầu.                                                    |
| 🤖 AI Assistant          | Trợ lý thông minh giải đáp thắc mắc tức thời, hỗ trợ người dùng trong mọi giai đoạn sáng tạo.                                                                              |
| 🌟 Image Enhancement     | Nâng cấp chất lượng hình ảnh đầu vào lên mức vượt trội bằng công nghệ độc quyền, làm nổi bật chi tiết và màu sắc.                                                          |
| 🎙️ Speech-to-Text (STT)  | Chuyển đổi file âm thanh thành văn bản chính xác, tự động nhận diện ngôn ngữ, nổi bật với hiệu suất cao cho tiếng Việt.                                                    |
| 📑 Trích xuất thông tin  | Phân tích và trích xuất dữ liệu từ âm thanh, video, hoặc file tài liệu với độ chính xác cao.                                                                               |
| 🧑‍🔧 Quản lý người dùng    | Cung cấp hệ thống tài khoản linh hoạt với vai trò (Free, Plus, Pro), kèm gói miễn phí và trả phí với giới hạn và quyền lợi riêng biệt.                                     |
| 🌐 Đa ngôn ngữ           | Hỗ trợ xử lý và hiển thị đa ngôn ngữ, với ưu tiên đặc biệt tối ưu hóa tiếng Việt.                                                                                          |
| 👮 Zero Trust            | Xác thực, phân quyền từng request từ user và kể cả các request nội bộ, request đến API để đảm bảo tính bảo mật                                                             |

---

## 🧑‍💻 Kiến trúc hệ thống

Hệ thống "Text to Everything" được thiết kế theo kiến trúc mô-đun, bao gồm các thành phần chính:

```
Client (React/Vite + HTML/CSS/Tailwind/JS)
│
│ (HTTP/WebSocket Requests)
▼
FastAPI Backend (Python)
│ ───────────────────────────────────────────────────────────────────────────┐
│ (Logic xử lý chính, Quản lý tác vụ, Xác thực, Phân quyền, API Gateway,.. ) │
│   ├──► Kết nối PostgreSQL (Dữ liệu người dùng, metadata, cấu hình)         │
│   ├──► Lưu trữ file (Input/Output từ người dùng)                           │
│   └──► Gọi External AI APIs (OpenAI, CloudFlare, v.v.)                     │
│       └──► Gọi Text-to-Speech Backend (Python FastAPI)                     │
│            ├──► TTS Default                                                │
│            └──► TTS with Voice Cloning (Vi-XTTS)                           │
▼
PostgreSQL Online Database
(Dữ liệu người dùng, metadata, cấu hình, input, output,...)
```

### 📑 Chi tiết thành phần

-   **Client**: Giao diện người dùng được phát triển bằng **React/Vite** kết hợp **HTML/CSS/Tailwind/JS**, xây dựng theo mô hình **Single Page Application (SPA)**, cung cấp trải nghiệm tương tác mượt mà và trực quan.
-   **FastAPI Backend**: Trụ cột chính sử dụng **Python FastAPI**, đảm nhận:
    -   Xử lý logic nghiệp vụ chính.
    -   Quản lý tác vụ, xác thực và phân quyền người dùng.
    -   Kết nối với **PostgreSQL** để lưu trữ dữ liệu người dùng, metadata, và cấu hình.
    -   Lưu trữ file input/output từ người dùng (hình ảnh, video, âm thanh).
    -   Gọi các **API bên thứ ba** (OpenAI, CloudFlare, v.v.) để tích hợp tính năng AI.
-   **Text-to-Speech Backend**: Một dự án phụ biệt lập sử dụng **Python FastAPI**, được thiết kế riêng để hỗ trợ:
    -   **TTS Default**: Tạo giọng nói tự nhiên từ văn bản.
    -   **TTS with Voice Cloning**: Sử dụng mô hình **Vi-XTTS** để sao chép giọng nói tùy chỉnh của người dùng.
    -   Backend này được FastAPI chính gọi để cung cấp tính năng TTS chuyên sâu.
-   **External AI APIs**: Tích hợp các dịch vụ từ **OpenAI**, **CloudFlare**, và các nhà cung cấp khác để mở rộng khả năng AI cho web app.
-   **PostgreSQL Database**: Lưu trữ dữ liệu có cấu trúc, bao gồm thông tin người dùng, metadata nội dung, và cấu hình hệ thống,...

### 🛠 Luồng hoạt động

1. **Client**: Người dùng tương tác qua giao diện SPA, gửi yêu cầu qua HTTP/WebSocket.
2. **FastAPI Backend**: Nhận yêu cầu, xác thực người dùng, điều phối đến các module xử lý, và lưu trữ dữ liệu/file.
3. **Text-to-Speech Backend**: Xử lý riêng biệt các tác vụ TTS (default và voice cloning) khi được gọi.
4. **External APIs**: Cung cấp hỗ trợ AI bổ sung từ các dịch vụ bên ngoài.
5. **PostgreSQL**: Đảm bảo lưu trữ và truy xuất dữ liệu hiệu quả.

Kiến trúc này cho phép mở rộng linh hoạt, đặc biệt với mô-đun TTS riêng biệt, đồng thời tối ưu hóa hiệu suất và khả năng bảo trì.

---

## 🛠 Công nghệ sử dụng

Dự án **Text to Everything** tận dụng các công nghệ hiện đại và tối ưu để đảm bảo hiệu suất, khả năng mở rộng và trải nghiệm người dùng vượt trội. Dưới đây là danh sách các công nghệ cốt lõi và lý do lựa chọn:

| Thành phần        | Công nghệ                           | Lý do lựa chọn                                                                                                                                   |
| ----------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Backend**       | Python 3.11+, FastAPI               | Python 3.11+ cung cấp hiệu năng vượt trội và hệ sinh thái AI/ML phong phú; FastAPI đảm bảo tốc độ cao, tự động tạo tài liệu API (Swagger/ReDoc). |
| **Frontend**      | React + Vite                        | React mang đến giao diện tương tác mạnh mẽ; Vite tối ưu hóa tốc độ phát triển và tải trang nhanh.                                                |
| **Cơ sở dữ liệu** | PostgreSQL                          | Hỗ trợ mạnh mẽ cho dữ liệu phức tạp, đáng tin cậy, và phù hợp với ứng dụng đa năng như Text to Everything.                                       |
| **AI Models**     | OpenAI, Stability AI, Vi-XTTS, v.v. | Tận dụng các mô hình State-of-the-Art (SOTA) từ OpenAI, Stability AI, và mô hình Vi-XTTS tự phát triển để xử lý đa dạng tác vụ AI.               |
| **Xác thực**      | OAuth2, JWT                         | Đảm bảo an toàn và linh hoạt trong quản lý đăng nhập, xác thực người dùng và service với tiêu chuẩn công nghiệp.                                 |
| **Triển khai**    | Docker, Railway, Render, Heroku     | Docker đóng gói ứng dụng đồng nhất; Railway, Render, Heroku cung cấp hạ tầng linh hoạt và dễ triển khai.                                         |
| **Lưu trữ file**  | FastAPI Backend                     | Tự thiết kế cơ chế lưu trữ file ở backend để dễ dàng quản lý, truy vấn và sử dụng lại khi cần.                                                   |
| **Linting**       | Black, Flake8, isort                | Đảm bảo mã nguồn nhất quán, dễ đọc và tuân thủ các tiêu chuẩn code style.                                                                        |

---

## 📦 Cài đặt và chạy dự án

### Điều kiện tiên quyết

-   **Python**: 3.11 hoặc cao hơn.
-   **Pip**: Đi kèm với Python.
-   **Git**: Quản lý phiên bản.
-   **PostgreSQL**: Cài đặt và tạo database (nếu chạy database online thì không cần).
-   **(Tùy chọn)** Docker & Docker Compose.

### Các bước cài đặt

1. **Clone dự án**:

    ```bash
    git clone https://github.com/vobao-xD/NT208__Project__Text-to-everything.git
    cd NT208__Project__Text-to-everything
    ```

2. **Tạo và kích hoạt môi trường ảo**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    venv\Scripts\activate     # Windows
    ```

3. **Cài đặt dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Cấu hình môi trường

1. **Tạo file `.env`**:

    ```bash
    cp .env.example .env  # Nếu có file mẫu
    ```

    Nếu không, tạo thủ công file `.env`.

2. **Cấu hình biến môi trường**:

    ```env
    # API Keys
    TTS_API_KEY=your_tts_api_key
    TTI_API_KEY=your_tti_api_key
    OPENROUTER_API_KEY=your_openrouter_api_key
    OPENAI_API_KEY=your_openai_api_key

    # Database
    DATABASE_URL=postgresql://user:password@localhost:5432/dbname

    # OAuth
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret

    # Redis
    REDIS_URL=redis://localhost:6379

    # SMTP
    SMTP_SERVER=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USERNAME=your_email
    SMTP_PASSWORD=your_app_password
    ```

    **Lưu ý**: Liên hệ nhóm hoặc tra cứu API key từ nhà cung cấp (OpenAI, Google, v.v.).

### Khởi chạy ứng dụng

-   **Backend**:

    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

    Truy cập: `http://localhost:8000/docs`.

-   **Frontend**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
    Truy cập: `http://localhost:5173`.

---

## 🧪 Tài liệu API

FastAPI tự động tạo tài liệu OpenAPI. Truy cập:

-   **Swagger UI**: `http://localhost:8000/docs`
-   **ReDoc**: `http://localhost:8000/redoc`

**Ví dụ endpoint**:

-   **POST /auth/register**: Đăng ký tài khoản.
    -   Body: `{"email": "user@example.com", "password": "pass"}`
-   **POST /text-to-speech/default**: Tạo giọng nói.
    -   Body: `{"text": "Xin chào", "language": "vi"}`
    -   Response: URL file âm thanh.

---

## 👤 Tài khoản và phân quyền

| Vai trò  | Quyền lợi                                                                                              | Giới hạn                                                                                  |
| -------- | ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| **Free** | Sử dụng API-Model 1 để tạo nội dung cơ bản, hỗ trợ cả chế độ tự động và thủ công linh hoạt             | Không hỗ trợ upload file để xử lý và không bao gồm mô hình API-Model 1.1 mới, mạnh mẽ hơn |
| **Plus** | Bao gồm tất cả quyền lợi của gói Free, bổ sung thêm tính năng upload file và hỗ trợ cao cấp            | Không bao gồm quyền truy cập vào mô hình API-Model 1.1 mới nhất                           |
| **Pro**  | Bao gồm toàn bộ quyền lợi của gói Plus, đồng thời truy cập đầy đủ mô hình API-Model 1.1 mới và mạnh mẽ |                                                                                           |

---

## 📊 Demo và minh họa (xem chi tiết hơn qua video demo (link drive))

-   **Giao diện Home Page của app (trước khi đăng nhập)**: Giới thiệu tổng quan về Web App Text to Everything.

    ![Giao diện Home Page](_demo_resources/home_page.png)

-   **Giao diện đăng nhập/đăng ký**: Cho phép đăng ký/đăng nhập bằng 3 hình thức (tài khoản ứng dụng, tài khoản Google, tài khoản Github).

    ![Giao diện Đăng nhập/Đăng ký](_demo_resources/login_sign_up.png)

-   **Giao diện Home Page của app sau khi đăng nhập**: Nơi để người dùng nhập input và nhận kết quả, sử dụng dịch vụ của app.

    ![Giao diện Home Page After Login](_demo_resources/after_login_home_page.png)

-   **Giao diện tính năng Auto Analyze**: tự động trích xuất yêu cầu của người dùng từ prompt và thực hiện chức năng tương ứng.

    ![Giao diện Auto Analyze](_demo_resources/analyze_1.png)
    ![Giao diện Auto Analyze](_demo_resources/analyze_2.png)
    ![Giao diện Auto Analyze](_demo_resources/analyze_3.png)

-   **Giao diện tính năng Text to Speech With Default Voice**: chuyển đổi văn bản thành giọng với với các giọng được cung cấp sẵng hoặc người dùng tự upload giọng của mình lên.

    ![Giao diện Text to Speech Default](_demo_resources/text_to_speech.png)

-   **Giao diện tính năng Text to Image**: chuyển đổi văn bản thành hình ảnh với chất lượng cao, nét vẽ đẹp, tạo ảnh mô tả cho văn bản

    ![Giao diện Text to Image](_demo_resources/text_to_image.png)

-   **Giao diện tính năng Text to Video**: chuyển đổi văn bản thành video ngắn với chất lượng ổn định, đồ họa bắt mắt

    ![Giao diện Text to Video](_demo_resources/text_to_video.png)

-   **Giao diện tính năng Image Quality Enhancing**: sử dụng công nghệ độc quyền để cải thiện chất lượng hình ảnh bằng cách tinh chỉnh các thông số như độ sáng, độ nét,...

    ![Giao diện trước Image Enhancer](_demo_resources/before_image_enhancer.png)
    ![Giao diện sau Image Enhancer](_demo_resources/after_image_enhancer.png)

-   **Giao diện tính năng AI Chatbot sáng tạo nội dung**: tạo content, viết truyện, kịch bản phim, làm thơ,...

    ![Giao diện AI Chatbot](_demo_resources/content_generate_chatbot.png)

-   **Giao diện tính năng AI Chatbot Assistant**: hỗ trợ tri thức và giải đáp thắc mắc cho người sử dụng

    ![Giao diện AI Assistant](_demo_resources/generate_answer.png)

-   **Giao diện tính năng Code Generator**: viết các chương trình, phần mềm bằng ngôn ngữ lập trình tùy chỉnh, hỗ trợ đắc lực cho developer

    ![Giao diện Code Generator](_demo_resources/code_generator.png)

-   **Giao diện tính năng trích xuất thông tin từ âm thanh**: trích xuất text từ các loại file audio

    ![Giao diện Speech to Text](_demo_resources/speech_to_text.png)

-   **Giao diện tính năng trích xuất thông tin từ video**: trích xuất text và cả ngữ cảnh từ các loại file video

    ![Giao diện Video to Text](_demo_resources/video_to_text.png)

-   **Giao diện tính năng trích xuất thông tin từ file (pdf, txt,...)**: trích xuất thông tin từ nhiều loại file đầu vào khác nhau

    ![Giao diện File to Text](_demo_resources/file_to_text.png)

-   **Video Demo**:
    [Link Drive](https://drive.google.com/drive/folders/1Tzi-JuDX_c6AOfSXEGv8iiPp3Syrj9B3?usp=sharing)

---

## 💡 Đóng góp

Chúng tôi hoan nghênh đóng góp từ cộng đồng!

-   **Báo lỗi**: Tạo Issue trên GitHub với chi tiết (bước tái hiện, log, ảnh chụp màn hình).
-   **Đề xuất tính năng**: Tạo Issue với nhãn "enhancement".
-   **Đóng góp mã**: Fork repo, tạo branch, đẩy code, mở Pull Request.
-   **Cải thiện tài liệu**: Cập nhật README hoặc docs qua PR.

---

## 📄 Giấy phép (License)

Dự án được cấp phép bởi Đại Học Công Nghệ Thông Tin (UIT).

---

## 📞 Liên hệ

-   **Email**: 23520146@gm.uit.edu.vn (Võ Quốc Bảo - nhóm trưởng)
-   **GitHub Issues**: Báo lỗi hoặc thảo luận tại repository.
-   **Thời gian**: Luôn sẵn sàng hỗ trợ!

---
