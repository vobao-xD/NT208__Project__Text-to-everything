import re
from collections import Counter

def guess_ai_intent(user_input):
    """
    Hàm đoán ý định người dùng muốn sử dụng AI để tạo loại nội dung nào
    
    Args:
        user_input (str): Chuỗi đầu vào từ người dùng
    
    Returns:
        str: Ý định chính của người dùng (generate_image, generate_video, generate_text, 
             generate_code, generate_speech, generate_unknown)
    """
    # Chuyển thành chữ thường để dễ xử lý
    text = user_input.lower()
    
    # Các từ khóa và pattern đặc trưng cho từng loại ý định
    intent_keywords = {
        'generate_image': [
            r'\b(vẽ|tạo|tạo ra|tạo một|thiết kế|chỉnh sửa|vẽ giúp|vẽ cho|tạo cho|tạo giúp).*?(ảnh|hình|hình ảnh|bức tranh|logo|biểu tượng|avatar|banner|poster|ảnh nền|thumbnail)\b',
            r'\b(ảnh|hình|hình ảnh|bức tranh|logo|biểu tượng|avatar|banner|poster|ảnh nền|thumbnail).*?(của|về|chủ đề)\b',
            r'\b(midjourney|dall-e|stable diffusion|dall e|dalle)\b',
            r'\b(phong cách|style|chất lượng cao|độ phân giải|resolution|px|pixel|ảnh chân dung|ảnh phong cảnh)\b',
            r'\bphát triển/tạo.*?(ảnh|hình)\b'
        ],
        'generate_video': [
            r'\b(tạo|làm|sản xuất|dựng|biên tập).*?(video|phim|clip|animation|hoạt hình|video ngắn|motion|hiệu ứng chuyển động)\b',
            r'\b(video|phim|clip|animation|hoạt hình|quay phim|chỉnh sửa video)\b',
            r'\b(hiệu ứng|chuyển cảnh|transition|render|xuất video|fps|frame|đoạn phim)\b',
            r'\b(gen-2|runway|sora|pika labs|d-id|synthesia|heygen)\b'
        ],
        'generate_text': [
            r'\b(viết|soạn|tạo|tạo ra|viết cho|viết giúp|soạn giúp|soạn cho).*?(văn bản|bài viết|email|thư|báo cáo|bài báo|blog|story|truyện|kịch bản|caption|nội dung|content)\b',
            r'\b(nội dung|content|văn bản|bài viết|thư từ|email|văn học|đoạn văn|blog|seo|email marketing)\b',
            r'\b(dịch|dịch thuật|dịch giúp|dịch cho|dịch sang|dịch qua|dịch từ).*?(tiếng|ngôn ngữ|văn bản|nội dung)\b',
            r'\b(gpt-4|gpt-3|chatgpt|bard|claude|copilot|gemini)\b',
            r'\b(tóm tắt|tổng hợp|phân tích|viết lại|paraphrase|rewrite|summarize)\b'
        ],
        'generate_code': [
            r'\b(viết|tạo|phát triển|code|coding|lập trình|debug|sửa lỗi).*?(code|mã|script|hàm|function|class|module|program|app|ứng dụng)\b',
            r'\b(python|javascript|java|c\+\+|php|html|css|sql|bash|ruby|golang|swift|kotlin|rust|typescript)\b',
            r'\b(algorithm|thuật toán|giải thuật|function|hàm|class|lớp|object|đối tượng|framework|library|thư viện)\b',
            r'\b(github|gitlab|bitbucket|stackoverflow|IDE|VSCode|PyCharm|IntelliJ|Xcode)\b'
        ],
        'generate_speech': [
            r'\b(tạo|sản xuất|tạo ra|chỉnh sửa|mix|master).*?(nhạc|âm thanh|audio|bài hát|giai điệu|beat|voice|giọng nói|podcast)\b',
            r'\b(nhạc|âm thanh|audio|bài hát|giai điệu|beat|voice|giọng nói|podcast|soundcloud|spotify)\b',
            r'\b(elevenlabs|murf|play\.ht|resemble\.ai|descript|sound|âm thanh|nhạc nền|beat|melody|harmony|nhịp điệu)\b',
            r'\b(chuyển.*?(văn bản|text).*?(thành|sang).*?(speech|giọng nói|giọng đọc|âm thanh|audio|voice))\b',
            r'\b(text-to-speech|tts|speech-to-text|stt|voice cloning|nhân bản giọng nói)\b'
        ],
        'chatbot': [
            r'\b(tạo|làm|phát triển|xây dựng|thiết kế).*?(chatbot|trợ lý ảo|bot|trợ lý|AI trò chuyện|AI giao tiếp)\b',
            r'\b(chatbot|trợ lý ảo|bot|trợ lý|AI trò chuyện|AI giao tiếp|trả lời tự động|conversational AI)\b',
            r'\b(dialogflow|rasa|botpress|wit\.ai|trò chuyện|chat|đối thoại|interact|interaction)\b',
            r'\b(hỗ trợ khách hàng|customer support|trả lời câu hỏi|FAQ bot|live chat)\b'
        ],
        'improve_image': [
            r'\b(cải thiện|nâng cấp|tăng chất lượng|chỉnh sửa|optimize|tối ưu hóa|enhance|retouch).*?(ảnh|hình|hình ảnh|image)\b',
            r'\b(xóa nền|remove background|tăng độ phân giải|upscale|sharpen|làm nét|denoise|khử nhiễu|restore|khôi phục).*?(ảnh|hình|hình ảnh)\b',
            r'\b(photoshop|lightroom|canva|fotor|pixlr|ảnh chất lượng thấp|low quality image)\b',
            r'\b(nâng cấp ảnh cũ|old photo restoration|colorize|lên màu|ảnh đen trắng|black and white)\b'
        ],
        'create_avatar': [
            r'\b(tạo|tạo ra|vẽ|thiết kế).*?(avatar|hình đại diện|nhân vật|character|profile picture|ảnh đại diện)\b',
            r'\b(avatar|hình đại diện|nhân vật|character|profile picture|ảnh đại diện|3d avatar|cartoon avatar|animated avatar)\b',
            r'\b(bitmoji|zepeto|toonme|avatarify|cartoonize|hoạt hình hóa|nhân vật ảo)\b',
            r'\b(tạo nhân vật cho|create character for|avatar cho|avatar for).*?(game|trò chơi|mạng xã hội|social media)\b'
        ]
    }
    
    # Đếm số pattern khớp cho mỗi loại ý định
    intent_matches = Counter()
    intent_details = {}
    
    for intent, patterns in intent_keywords.items():
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text)
            if found:
                matches.extend(found)
        
        intent_matches[intent] = len(matches)
        intent_details[intent] = matches
    
    # Xác định ý định chính
    if sum(intent_matches.values()) == 0:
        return "generate_answer"
    else:
        # Trả về ý định có số lượng match nhiều nhất
        primary_intent = intent_matches.most_common(1)[0][0]
        return primary_intent