MCQA_QUESTION_GENERATION_PROMPT = """Bạn là một chuyên gia xây dựng câu hỏi trắc nghiệm trong lĩnh vực **{domain}**. Nhiệm vụ của bạn là tạo ra {num_questions} câu hỏi trắc nghiệm dựa trên nội dung tham khảo dưới đây (và bạn phải giữ bí mật nội dung tham khảo này, không được tiết lộ rằng bạn được cung cấp nội dung này, đồng thời không được sử dụng các cụm từ như "theo tài liệu", "theo nội dung"):

**Đoạn văn:**  
{content}

### Yêu cầu

Sinh các câu hỏi trắc nghiệm đa dạng bằng Tiếng Việt.

Các câu hỏi PHẢI hoàn toàn dựa trên nội dung tham khảo và KHÔNG được viện dẫn hay nhắc đến nguồn tham khảo.

Các câu hỏi được tạo cần bao gồm sự kết hợp của các dạng suy luận sau:

- Truy xuất thông tin thực tế trực tiếp (20-30%)
- Kiểm tra tính đúng sai của nhiều nhận định (20-30%)
- Câu hỏi phủ định yêu cầu xác định nhận định sai hoặc không đúng (20-30%)
- Suy luận nguyên nhân - kết quả
- Suy luận ngầm và rút ra kết luận

Tránh chỉ tạo các câu hỏi tra cứu thông tin đơn giản.

Đối với các câu hỏi suy luận dựa trên nhiều nhận định:
- Tạo từ 3-5 nhận định.
- Một số nhận định phải đúng và một số phải sai.
- Các phương án trả lời phải chứa các tổ hợp khác nhau của các chỉ số nhận định.
- Chỉ có duy nhất một phương án đúng.

Ví dụ:

Những nhận định nào sau đây đúng?

1. ...
2. ...
3. ...
4. ...

A. 1 và 2
B. 2 và 4
C. 1, 3 và 4
D. 3 và 4

HOẶC

Nhận định nào sau đây KHÔNG đúng?

A. ...
B. ...
C. ...
D. ...

Câu hỏi cần yêu cầu người đọc phải đọc hiểu và suy luận cẩn thận thay vì chỉ tìm một câu thông tin đơn lẻ.

Các phương án nhiễu phải hợp lý và dựa trên các thực thể, mốc thời gian, sự kiện hoặc khái niệm xuất hiện trong đoạn văn.

Mỗi câu hỏi phải có chính xác một đáp án đúng.

### Định dạng phản hồi:

Với mỗi câu hỏi, hãy cung cấp nội dung câu hỏi, bốn phương án trả lời và đáp án đúng theo định dạng sau:

1.
<question>
Nội dung câu hỏi
A. Phương án A
B. Phương án B
C. Phương án C
D. Phương án D
</question>
<choice>Đáp án đúng của Câu 1</choice>

2.
<question>
Nội dung câu hỏi
A. Phương án A
B. Phương án B
C. Phương án C
D. Phương án D
</question>
<choice>Đáp án đúng của Câu 2</choice>

... (lặp lại cho đến đủ số lượng câu hỏi được yêu cầu)
"""