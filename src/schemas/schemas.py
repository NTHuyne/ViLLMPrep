from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ResponseSFTItem(BaseModel):
    """
    Represents a question and answer pair.

    Attributes:
        question (str): Question.
        answer (str): Answer.
        id (str): Id of the question.
        question_type (str): Type of the question.
        domain (str): Domain of the question.
        original_document (str): Original document.
        data_type (str): Type of data.
    """
    question: str = Field(
        title="Câu hỏi"
    )
    answer: str = Field(
        title="Câu trả lời"
    )
    id: str = Field(   
        title="Id của câu hỏi"
    )
    question_type: str = Field(
        title="Loại câu hỏi: 'tuluan' hoặc 'tracnghiem'"
    )
    domain: str = Field(    
        title="Lĩnh vực của câu hỏi"
    )
    original_document: str = Field(
        title="Tài liệu gốc"
    )
    data_type: str = Field(
        title="Loại dữ liệu",
        description="Loại dữ liệu: 'train' hoặc 'test'"
    )   


class ResponseDPOItem(BaseModel):
    """
    Represents a question and answer pair.

    Attributes:
        question (str): Question.
        answer (str): Answer.
        id (str): Id of the question.
        question_type (str): Type of the question.    
        domain (str): Domain of the question.
    """
    question: str = Field(
        title="Câu hỏi"
    )
    accepted_answer: str = Field(
        title="Câu trả lời được chấp nhận"
    )
    rejected_answer: str = Field(
        title="Câu trả lời bị từ chối"
    )
    id: str = Field(   
        title="Id của câu hỏi"
    )
    domain: str = Field(    
        title="Lĩnh vực của câu hỏi"
    )
    original_document: str = Field(
        title="Tài liệu gốc"
    )


class ChunkItem(BaseModel):
    """
    Represents a chunk of data with associated metadata.

    Attributes:
        chunk_id (str): Id of the input chunk.
        parent_id (str): Id of the file containing the input chunk.
        content (str): Content of the input chunk.
        domain (str): Domain of the input chunk.
    """
    chunk_id: str = Field(
        title="Id của chunk đầu vào"
    )
    parent_id: str = Field(
        title="Id của file chưa chunk đầu vào"
    )
    content: str = Field(
        title="Nội dung của chunk đầu vào"
    )
    domain: str = Field(    
        title="Lĩnh vực của chunk đầu vào"
    )


class SFTGenerationRequest(BaseModel):
    """
    Request sinh dữ liệu SFT.
    Các tham số cấu hình được lấy từ config server nên không bắt buộc truyền vào.
    """

    generative_model: Optional[str] = Field(
        default=None,
        title="Mô hình sinh dữ liệu"
    )

    base_url: Optional[str] = Field(
        default=None,
        title="Endpoint của mô hình sinh dữ liệu"
    )

    chunk_data: List[ChunkItem] = Field(
        title="Dữ liệu chunk đầu vào"
    )

    num_essay_train_samples: Optional[int] = Field(
        default=None,
        title="Số lượng mẫu câu hỏi tự luận huấn luyện cần sinh"
    )

    num_mcqa_train_samples: Optional[int] = Field(
        default=None,
        title="Số lượng mẫu câu hỏi trắc nghiệm huấn luyện cần sinh"
    )

    num_essay_test_samples: Optional[int] = Field(
        default=None,
        title="Số lượng mẫu câu hỏi tự luận đánh giá cần sinh"
    )

    num_mcqa_test_samples: Optional[int] = Field(
        default=None,
        title="Số lượng mẫu câu hỏi trắc nghiệm đánh giá cần sinh"
    )


class DPOGenerationRequest(BaseModel):
    """
    Request sinh dữ liệu DPO.
    Các tham số cấu hình được lấy từ config server nên không bắt buộc truyền vào.
    """

    generative_model: Optional[str] = Field(
        default=None,
        title="Mô hình sinh dữ liệu"
    )

    base_url: Optional[str] = Field(
        default=None,
        title="Endpoint của mô hình sinh dữ liệu"
    )

    chunk_data: List[ChunkItem] = Field(
        title="Dữ liệu chunk đầu vào"
    )

    num_samples: Optional[int] = Field(
        default=None,
        title="Số lượng mẫu câu hỏi cần sinh"
    )


class InvalidInputResponse(BaseModel):
    """
    Represents a response for invalid input data.
    """
    detail: List[Any] = Field(..., description = "Thông báo lỗi khi dữ liệu đầu vào không hợp lệ")
    body: Dict[str, Any] = Field(..., description = "Dữ liệu đầu vào không hợp lệ")


ERRORS_EXTRA = """
0: "Lỗi không xác định"\n
1: "Lỗi từ module AI"
"""
class InternalServerErrorResponse(BaseModel):
    """
    Represents a response for internal server error.
    """
    code: int = Field(..., description = "Mã lỗi của dự án:\n" + ERRORS_EXTRA)
    message: str = Field(..., description = "Thông báo lỗi của dự án")


class ResponseSFT(BaseModel):
    """
    Represents a response for SFT data generation.

    Attributes:
        data (ResponseSFTItem): Generated data.
    """
    data: ResponseSFTItem = Field(
        title="Dữ liệu SFT sinh ra"
    )


class ResponseDPO(BaseModel):
    """
    Represents a response for DPO data generation.

    Attributes:
        data (ResponseDPOItem): Generated data.
    """
    data: ResponseDPOItem = Field(
        title="Dữ liệu DPO sinh ra"
    )
