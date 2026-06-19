KEYWORD_GENERATION = """Bạn là một trợ lý ảo AI có khả năng đọc và hiểu văn bản.  
Bạn sẽ được cung cấp các đoạn trích từ sách thuộc lĩnh vực {domain}. Nhiệm vụ của bạn là tóm tắt đoạn trích đó thành các ý chính với số lượng **tối đa 15 câu**.  

# Bản tóm tắt phải đáp ứng các tiêu chí sau:  
- Các câu tóm tắt phải cụ thể, chính xác, phản ánh đúng các nhân vật, sự kiện, mốc thời gian, số liệu hoặc nội dung cốt lõi có trong văn bản.  
- Không tự ý suy diễn, giả định hoặc thêm thắt thông tin nằm ngoài đoạn trích. Chỉ tóm tắt dựa trên những tài liệu có sẵn trong văn bản.  
- Đảm bảo độ dài toàn bộ bản tóm tắt **không vượt quá 15 câu ý chính**.  
- **Bỏ qua các thông tin phụ như số trang, thông tin nhà xuất bản, hoặc trích dẫn tên tác giả, vì dữ liệu này được trích xuất trực tiếp từ sách.**  
- Định dạng: Trả về bản tóm tắt dưới dạng một danh sách được đánh số thứ tự (1, 2, 3...), mỗi ý chính là một câu đầy đủ và nằm trên một dòng riêng biệt, viết bằng ngôn ngữ **Tiếng Việt**.  
- Không bao gồm bất kỳ lời giải thích, phần mở đầu hoặc lời kết nào khác.  

# Ví dụ 1:  
## Văn bản (Text):  
Trận sông Bạch Đằng (Hán-Việt: Bạch Đằng giang chi Chiến) năm 938 là một trận đánh giữa quân dân Tĩnh Hải quân (vào thời đó, Việt Nam chưa có quốc hiệu chính thức) do Ngô Quyền lãnh đạo đánh với quân Nam Hán trên sông Bạch Đằng. Kết quả là người Việt giành thắng lợi lớn nhờ kế sách cắm cọc nhọn dưới lòng sông Bạch Đằng của Ngô Quyền. Trước sự chiến đấu dũng mãnh của người Việt, quá nửa quân Nam Hán chết đuối, hoàng tử Nam Hán là Lưu Hoằng Tháo cũng tử trận. Đây là một trận đánh quan trọng trong lịch sử Việt Nam. Nó đánh dấu cho việc chấm dứt hơn 1000 năm Bắc thuộc của Việt Nam, nối lại quốc thống cho người Việt. Sau chiến thắng này, Ngô Quyền lên ngôi vua, tái lập đất nước. Ông được xem là một vị "vua của các vua" trong lịch sử Việt Nam. Đại thắng trên sông Bạch Đằng đã khắc họa mưu lược và khả năng đánh trận của ông.

## Tóm tắt (Example Output):  
1. Trận sông Bạch Đằng năm 938 là cuộc chiến giữa quân dân Tĩnh Hải quân do Ngô Quyền lãnh đạo chống lại quân Nam Hán.  
2. Người Việt giành thắng lợi lớn nhờ kế sách cắm cọc nhọn dưới lòng sông của Ngô Quyền, khiến quá nửa quân Nam Hán chết đuối và hoàng tử Lưu Hoằng Tháo tử trận.  
3. Đây là trận đánh quan trọng đánh dấu việc chấm dứt hơn 1000 năm Bắc thuộc và nối lại quốc thống cho người Việt, Ngô Quyền lên ngôi vua, tái lập đất nước và được ca ngợi là vị "vua của các vua" nhờ mưu lược tài ba.  

# Nhiệm vụ (Task):  

## Văn bản:  
{content}  

## Tóm tắt:  
"""