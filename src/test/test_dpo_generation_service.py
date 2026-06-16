import asyncio
from src.schemas.schemas import DPOGenerationRequest, ChunkItem
from src.functions.dpo_generation_service import generate_dpo_data

async def test_generate_dpo_data():
    """
    Test the generate_dpo_data function with a sample chunk.
    This function creates a test chunk and request, then calls the generate_dpo_data
    function to generate DPO data. The results are printed for verification.
    """
    # Create a test chunk
    test_chunk = ChunkItem(
        chunk_id="0",
        parent_id="wiki",
        content="An toàn thông tin là hành động ngăn cản, phòng ngừa sự sử dụng, truy cập, tiết lộ, chia sẻ, phát tán, ghi lại hoặc phá hủy thông tin chưa có sự cho phép.",
        domain="An toàn thông tin"
    )

    test_chunk2 = ChunkItem(
        chunk_id="1",
        parent_id="wiki",
        content="Nhiều phần phim về chú mèo máy gây sốt khán giả châu Á, trong đó có Việt Nam. Năm 2024, phim thứ 43 Doraemon: Nobita và bản giao hưởng địa cầu đạt hơn 147 tỷ đồng, trở thành phim anime ăn khách nhất từ trước đến nay ở thị trường trong nước. Ở Nhật Bản, dự án thu 4,31 tỷ yên (29 triệu USD).",
        domain="Giải trí"
    )

    # Create a test request
    test_request = DPOGenerationRequest(
        generative_model="gpt-4o-mini",
        chunk_data=[test_chunk, test_chunk2],
        num_samples=2
    )

    # Call the generate_sft_data function
    dpo_data = await generate_dpo_data(test_request)

    # Print the results
    print(dpo_data)

# Run the test
if __name__ == "__main__":
    asyncio.run(test_generate_dpo_data())