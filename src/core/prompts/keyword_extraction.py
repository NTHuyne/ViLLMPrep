KEYWORD_GENERATION = """You are a virtual AI assistant capable of reading and understanding text.  
You will be provided with excerpts from books in the field of {domain}. Your task is to extract **important** keywords related to the given text.  

# The keywords must meet the following criteria:  
- The keywords must be specific enough to reference characters, events, or related content from the text.  
- Keywords can include character names, events, time periods, locations, numerical data, or quotes, as long as they are specific and accurate.  
- Do **not** generate keywords automatically. Extract only words present in the text. Avoid ambiguous or overly broad keywords.  
- **Exclude keywords that are not detailed or specific enough.**  
- **Ignore keywords related to page numbers, publishing information, or book author citations, as the data is extracted from books.**  
- Extract all possible keywords from each passage.  
- Format: Return the keywords as a list, separated by line breaks, numbered sequentially, and in the language **Tiếng Việt**.  
- Do not include any additional explanations.  

# Example 1:  
## Text:  
Trận sông Bạch Đằng (Hán-Việt: Bạch Đằng giang chi Chiến) năm 938 là một trận đánh giữa quân dân Tĩnh Hải quân (vào thời đó, Việt Nam chưa có quốc hiệu chính thức) do Ngô Quyền lãnh đạo đánh với quân Nam Hán trên sông Bạch Đằng. Kết quả là người Việt giành thắng lợi lớn nhờ kế sách cắm cọc nhọn dưới lòng sông Bạch Đằng của Ngô Quyền. Trước sự chiến đấu dũng mãnh của người Việt, quá nửa quân Nam Hán chết đuối, hoàng tử Nam Hán là Lưu Hoằng Tháo cũng tử trận. Đây là một trận đánh quan trọng trong lịch sử Việt Nam. Nó đánh dấu cho việc chấm dứt hơn 1000 năm Bắc thuộc của Việt Nam, nối lại quốc thống cho người Việt. Sau chiến thắng này, Ngô Quyền lên ngôi vua, tái lập đất nước. Ông được xem là một vị "vua của các vua" trong lịch sử Việt Nam. Đại thắng trên sông Bạch Đằng đã khắc họa mưu lược và khả năng đánh trận của ông.

## Keywords (Example Output):  
1. Quân Nam Hán  
2. Ngô Quyền  
3. Trận sông Bạch Đằng năm 938  
4. Lưu Hoằng Tháo  
5. Chấm dứt 1000 năm Bắc thuộc  

# Task:  

## Text:  
{content}  

## Keywords:  
"""
