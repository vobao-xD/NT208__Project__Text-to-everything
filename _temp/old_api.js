    // Xóa cuộc trò chuyện
    async deleteConversation(conversationId) {
        const token = Cookies.get("access_token");
        if (!token) throw new Error("Không tìm thấy token xác thực");
        const response = await fetch(
            `http://localhost:8000/chat-history/${conversationId}`,
            {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                credentials: "include",
            }
        );
        if (!response.ok)
            throw new Error(
                `Lỗi xóa cuộc trò chuyện: ${await response.text()}`
            );
        return { id: conversationId };
    },
    