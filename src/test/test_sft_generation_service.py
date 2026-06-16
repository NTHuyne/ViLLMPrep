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
        content='Triều đại nhà Trần là triều đại lẫy lừng trong lịch sử phong kiến Việt Nam. Triều đại nhà Trần bắt đầu bắt đầu khi vua Trần Thái Tông lên ngôi năm 1225 sau khi giành được quyền lực từ tay nhà Lý, trải qua 175 năm với 12 triều vua và thời hậu trần 7 năm có 2 đời vua. Có thể nói việc chuyển giao nhà Lý sang nhà Trần là một cuộc chuyển giao quyền lực nhẹ nhàng nhất trong lịch sử phong kiến nước ta. Bởi nhà Lý đã suy yếu, không thể tiếp tục sứ mệnh lãnh đạo đất nước của mình. Năm 1225, Trần Cảnh lên ngôi mở đầu cho vương triều nhà Trần. Nhà sử học Lê Văn Lan cho rằng Trần Thái Tông – vị vua đầu triều nhà Trần chính là người đã đặt nền móng cho một triều đại lừng lẫy trong lịch sử. Ngay từ khi lên ngôi, mở ra triều đại nhà Trần, vua Trần Thái Tông đã nhanh chóng khắc phục những hậu quả do khủng hoảng cuối nhà Lý gây ra, đặc biết ông khuyến khích nông dân khai hoang, chăm lo việc trị thủy, theo đuổi chính sách khoan thư sức dân. Những chính sách này đã thúc đẩy kinh tế nông nghiệp phát triển, đời sống nhân dân ấm no. Theo PGS.TS Sử học Nguyễn Thị Phương Chi thì đây là một triều đại biết trọng dụng nhân tài, biết thu phục lòng dân. Có thể nói, sự ra đời của nhà Trần thực sự là một bước ngoặt lớn của nước Đại Việt thời phong kiến. Nhà Trần cũng chính là triều đại đã làm nên hào khí Đông A – Vua tôi đồng lòng, anh em hòa thuận, cả nước chung sức xây dựng nên một triều đại lẫy lừng trong lịch sử dân tộc. Cũng có lúc lâm vào thế “ngàn cân treo sợi tóc”, tưởng như đất nước bị giày xéo dưới vó ngựa quân Nguyên Mông, thế nhưng nhờ sự sáng suốt của vị vua đầu triều và sự quả cảm của quần thần mà vận nước vẫn vững vàng sau 3 lần đánh thắng xâm lăng. PGS.TS Sử học Nguyễn Đức Nhuệ cho rằng một trong những lý do khiến nhà Trần được sử sách lưu danh và quan tâm nhiều nhất chính là những chiến thắng rực rỡ trước quân đội Mông Cổ mạnh hơn gấp nhiều lần. Quân dân nhà Trần 3 lần đánh tan quân xâm lược Nguyên Mông - Đế quốc phong kiến được coi là hùng mạnh nhất lúc bấy giờ Quân dân nhà Trần 3 lần đánh tan quân xâm lược Nguyên Mông - Đế quốc phong kiến được coi là hùng mạnh nhất lúc bấy giờ Không chỉ ghi danh sử sách 3 lần đánh thắng quân xâm lược Nguyên – Mông, triều Trần còn được coi là triều đại có nhiều công lao trị yên đất nước, đặc biệt là việc trấn giữ biên giới của quốc gia. Theo PGS.TS Sử học Nguyễn Đức Nhuệ, các chính sách ngoại giao của nhà Trần rất mềm dẻo nhưng cũng vô vùng cương quyết, thể hiện rõ lòng tự hào, tự tôn dân tộc. Ba lần kháng chiến chống quân Mông - Nguyên thế kỷ XIII của nước Đại Việt dưới triều Trần có ý nghĩa vô cùng quan trọng. Chiến thắng đó không chỉ khẳng định lòng yêu nước của người dân đất Việt từ ngàn đời mà còn thể hiện ý chí quyết tâm bảo vệ đất nước, chủ quyền lãnh thổ của dân tộc.',
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
