import asyncio
import json
from src.schemas.schemas import SFTGenerationRequest, ChunkItem
from src.functions.sft_generation_service import generate_sft_data
from src.configs.config import settings

async def test_generate_sft_data():
    """
    Test the generate_sft_data function with a sample chunk.
    This function creates a test chunk and request, then calls the generate_sft_data
    function to generate SFT data. The results are printed for verification.
    """
    # Create a test chunk
    test_chunk = ChunkItem(
        chunk_id="0",
        parent_id="Lịch sử Việt Nam",
        content="#### Chương I\n\n# TRIỀU NGUYỄN THIẾT LẬP NHÀ NƯỚC QUÂN CHỦ CHUYỂN CHẾ\n\n# I. TỔ CHỨC BỘ MÁY NHÀ NƯỚC\n\nSau khi thành lập, vương triều Nguyễn đã thừa hưởng được thành quả to lớn của phong trào nông dân Tây Sơn trong sự nghiệp thống nhất đất nước, làm chủ một lãnh thổ trải dài từ ải Nam Quan đến mũi Cà Mau, bao gồm cả Đàng Trong và Đàng Ngoài. Để xây dựng một vương triều vững mạnh, vua Gia Long phải giải quyết hài hòa nhưng thống nhất về chế độ chính trị khác nhau của ba miền trong buổi đầu dựng nghiệp¹. Do vậy, hệ thống chính quyền Trung ương thời Gia Long vẫn theo mô hình thời Lê, mặc dù vua Gia Long đã nói rõ chỉ là \"tạm đặt\" trong buổi đầu. Từ thời Minh Mệnh (1820 - 1840) việc cải tổ, kiện toàn và hoàn thiện bộ máy nhà nước mới được thực hiện một cách quy củ và triều đình Nguyễn thật sự trở thành một nhà nước quân chủ chuyên chế phát triển đến đình cao.\n\nVương triều Nguyễn được thành lập trong một bối cảnh chính trị - xã hội tương đối phức tạp. Nhà Nguyễn phải đối mặt với nhiều khó khăn trở ngại. Sự chia cắt Đàng Trong - Đàng Ngoài trong hơn hai thế kỷ đã tạo nên sự khác biệt nhất định về thể chế chính trị hai miền, về cách thức tổ chức và phương pháp quản lý. Nhà Tây Sơn tồn tại trong một thời gian ngắn, trên thực tế quyền lực bị phân tán nên chưa có điều kiện và khả năng tạo nên một mô hình tổ chức chính quyền thống nhất. Mặc dù dòng họ Nguyễn có nguồn gốc từ xứ Thanh, tổ tiên nhà Nguyễn gắn bó mật thiết với vương triều Lê-Trịnh nhưng có lẽ vua Gia Long cũng không thể hiểu một cách tường tận về đất Bắc Hà, về tâm lý \"hoài Lê\" của cựu thần nhà Lê và nhân dân Bắc Hà. Đây chính là những vấn đề mà Gia Long rất quan tâm và thận trọng khi tiến hành xây dựng mô hình bộ máy chính quyền buổi đầu.\n\nDưới thời Gia Long, nhà Nguyễn vẫn duy trì hệ thống các cơ quan trung ương: đứng đầu là vua - người nắm quyền hành cao nhất. Bên dưới là 6 bộ (Lại, Hộ, Lễ, Binh, Hình, Công), chịu trách nhiệm chỉ đạo các công việc chung của nhà nước và cùng với Ngũ quân Đô thống phủ phụ trách quân đội. Tuy tổ chức đủ 6 bộ nhưng phải đến năm Giáp Tý (1804), Gia Long mới cho đúc ấn của 6 bộ và đến năm Kỷ Ty (1809) mới đặt đủ chức quan của 6 bộ. Đứng đầu mỗi bộ là một viên Thượng thư 1, dưới chức Thượng thư có các chức Tả - Hữu Tham tri giúp việc. Tiếp đó là các chức Thiêm sự, Câu kê, Cai hợp, Thủ hợp... và nhân viên ở Lệnh sử ty, Bản ty. Ngoài ra, bộ máy chính quyền ở Trung ương còn có các cơ quan chuyên trách như: Ngự sử đài và hai tự (Thái thường tự và Thái bộc tư) giữ việc thanh tra, đàn hặc và giám sát; Tam nội viện (Thi thư viện, Thị hàn viện và Nội hàn viện) có chức trách ghi chép các chiếu dụ, văn thư, giấy tờ và giúp vua giải quyết các công việc; Thái y viện trông nom việc thuốc thang, chữa bệnh; Quốc tử giám phụ trách giáo dục; Khâm thiên giám phụ trách thiên văn, địa lý, lịch pháp...\n\nTriều đình Trung ương dưới thời Gia Long trực tiếp quản lý 4 dinh, 7 trấn từ Thanh Hoa ngoại đến Bình Thuận; còn phía Bắc từ Sơn Nam Hạ trở ra (11 nội, ngoại trấn) và phía Nam từ trấn Biên Hòa trở vào chỉ quản lý gián tiếp thông qua viên Tổng trấn Bắc thành và Gia Định thành. Đây là một \"biện pháp khôn khéo, linh hoạt của Gia Long trong buổi đầu nhằm thực hiện việc quản lý đất nước, đồng thời đảm bảo sự tồn tại an toàn của vương triều\". Tuy nhiên, trước xu hướng tập trung quyền lực của nhà nước quân chủ chuyên chế phương Đông mà vương triều Nguyễn kiên trì theo đuổi thì thực trạng trên của bộ máy chính quyền Trung ương thật sự còn đơn giản và chưa chặt chẽ về mặt thiết chế, đặc biệt là sự phân quyền trong việc quản lý một đất nước rộng lớn nhất từ trước đến giờ².\n\nDưới thời Minh Mệnh (1820-1840), để tăng cường quyền lực tập trung, Minh Mệnh rất có ý thức trong việc xây dựng và củng cố bộ máy nhà nước quân chủ Trung ương tập quyền chặt chẽ, quy củ. Công cuộc cải tổ được tiến hành dần dần nhưng quyết liệt bắt đầu từ bộ máy hành chính của các cơ quan Trung ương, sau đó đến các thể chế hành chính ở các địa phương. Bằng cách đặt ra một số cơ quan, tổ chức mới như Nội các, Cơ mật viện; bổ sung thêm chức Tham tri và Chủ sự ở các bộ; thay đổi Ngự sử đài (thời Lê) thành Đô sát viện, thay các chức Câu kê, Cai hợp bằng Thư lại; bãi bỏ Bắc thành và Gia Định thành, thiết lập đơn vị hành chính tinh với các chức Tổng đốc, Tuần phủ, Bố chính, Án sát...",
        domain="Lịch sử Việt Nam"
    )

    # Create a test request
    test_request = SFTGenerationRequest(
        generative_model=settings.MODEL_CONF['model_name'],
        base_url=settings.MODEL_CONF['base_url'],
        chunk_data=[test_chunk],
        num_essay_train_samples=20,
        num_mcqa_train_samples=5,
        num_essay_test_samples=0,
        num_mcqa_test_samples=0,
    )

    # Call the generate_sft_data function
    sft_data = await generate_sft_data(test_request)

    json_data = [r.model_dump() for r in sft_data]


    # Write to file
    with open("test.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

# Run the test
if __name__ == "__main__":
    asyncio.run(test_generate_sft_data())
