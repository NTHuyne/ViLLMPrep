MCQA_ANSWER_PROMPT = """Bạn sẽ được cung cấp một câu hỏi trắc nghiệm cùng với bốn phương án trả lời: A, B, C và D, đáp án đúng đã cho và tài liệu tham khảo (và bạn phải **giữ bí mật tài liệu tham khảo này**, không được tiết lộ rằng bạn được cung cấp tài liệu này và không được chứa các cụm từ như "theo tài liệu"). Hãy phân tích kỹ câu hỏi và tính đúng đắn của từng phương án, xác định đáp án chính xác nhất cho câu hỏi và giải thích cho lựa chọn của bạn. Câu trả lời của bạn phải trung thực, đầy đủ, dài và có giải thích chi tiết. Toàn bộ phản hồi phải bằng Tiếng Việt. Toàn bộ phản hồi phải bằng Tiếng Việt. Chỉ trả về câu trả lời.

## Nhiệm vụ của bạn
Reference Document: {content}

Question: {question}

Given Correct Answer: {choice}

Answer:
"""