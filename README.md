# ViLLMPrep

**Vi**etnamese **L**arge **L**anguage **M**odel data **Prep**aration.

Công cụ sinh dữ liệu huấn luyện cho LLM, tập trung vào dữ liệu tiếng Việt. Hỗ trợ sinh dữ liệu cho hai phương pháp:

- **SFT (Supervised Fine-Tuning)**: Sinh câu hỏi-tự luận và trắc nghiệm kèm câu trả lời.
- **DPO (Direct Preference Optimization)**: Sinh câu hỏi kèm cặp câu trả lời được chấp nhận / bị từ chối.

## Yêu cầu

- Python 3.10+
- Các thư viện trong `requirements.txt`

## Cài đặt

```bash
pip install -r requirements.txt
```

## Cấu hình

### 1. Cấu hình model LLM (`settings/llm_config.yaml`)

Mở file `settings/llm_config.yaml` và cập nhật các thông tin:

```yaml
model:
  api_key: "your-api-key"          # API key của LLM provider
  base_url: "https://api.openai.com/v1"  # Endpoint API
  model_name: "gpt-4o-mini"        # Tên model
  temperature: 0.4                 # Temperature cho generation
  provider: openai-compatible
```

Các tham số `--model` và `--base-url` trong CLI có thể ghi đè cấu hình trong file này.

### 2. Cấu hình service (`settings/service_config.yaml`)

File này chứa cấu hình chung của ứng dụng:

```yaml
api_keys:
  - AI_team
  
app:
  root_path: "/autogen/src"
```

> **Lưu ý:** Mặc định file `settings/llm_config.yaml` chứa các giá trị mẫu (`YOUR-API-KEY`, `base-url`, `model-name`). Bạn cần cập nhật các giá trị này trước khi chạy.

## Chuẩn bị dữ liệu đầu vào

### Input JSON format

```json
[
  {
    "chunk_id": "0",
    "parent_id": "source_document_id",
    "content": "Nội dung văn bản của chunk...",
    "domain": "Lĩnh vực (vd: Lịch sử Việt Nam)"
  },
  {
    "chunk_id": "1",
    "parent_id": "source_document_id",
    "content": "Nội dung chunk khác...",
    "domain": "Lĩnh vực khác"
  }
]
```

Ngoài ra, script cũng hỗ trợ **JSONL format** (một JSON object trên mỗi dòng).

## Pipeline và cơ chế Resume (phục hồi)

Cả hai script đều có cơ chế **resume tự động**: mỗi bước trong pipeline đều được lưu vào file JSON riêng trong thư mục output. Nếu một bước bị lỗi (do timeout, lỗi API, ...), bạn chỉ cần sửa lỗi và chạy lại cùng lệnh. Script sẽ **bỏ qua các bước đã hoàn thành** và tiếp tục từ bước bị gián đoạn.

**Các file trung gian được lưu trong thư mục output:**

### SFT intermediate files

| File | Nội dung |
|------|----------|
| `keywords.json` | Kết quả trích xuất từ khóa |
| `essay_questions.json` | Câu hỏi tự luận đã sinh |
| `essay_answers.json` | Câu trả lời tự luận đã sinh |
| `mcqa_questions.json` | Câu hỏi trắc nghiệm đã sinh |
| `mcqa_answers.json` | Câu trả lời trắc nghiệm đã sinh |
| **`sft_data.json`** | **Kết quả cuối cùng** |

### DPO intermediate files

| File | Nội dung |
|------|----------|
| `keywords.json` | Kết quả trích xuất từ khóa |
| `essay_questions.json` | Câu hỏi đã sinh |
| `dpo_answers.json` | Cặp accepted + rejected answers |
| **`dpo_data.json`** | **Kết quả cuối cùng** |

> **Lưu ý:** Bước đầu tiên (đọc file input) luôn chạy lại từ đầu, các bước sau có thể resume.

## Sinh dữ liệu SFT

Sử dụng script `src/generate_sft_data.py`:

```bash
# Cơ bản - dùng model từ llm_config.yaml
python src/generate_sft_data.py --input chunks.json --output ./sft_output

# Tùy chỉnh số lượng mẫu
python src/generate_sft_data.py \
    --input chunks.json \
    --output ./sft_output \
    --num-essay-train 20 \
    --num-essay-test 5 \
    --num-mcqa-train 10 \
    --num-mcqa-test 3

# Chỉ định model và base URL (ghi đè llm_config.yaml)
python src/generate_sft_data.py \
    --input chunks.json \
    --output ./sft_output \
    --model gpt-4o-mini \
    --base-url https://api.openai.com/v1

# Resume từ lần chạy bị gián đoạn (chạy lại cùng lệnh)
python src/generate_sft_data.py --input chunks.json --output ./sft_output
```

### Tham số SFT

| Tham số | Mô tả | Giá trị mặc định |
|---------|-------|-----------------|
| `--input` / `-i` | Đường dẫn file input JSON/JSONL | **Bắt buộc** |
| `--output` / `-o` | Đường dẫn thư mục output (không phải file) | **Bắt buộc** |
| `--num-essay-train` | Số mẫu câu hỏi tự luận cho training | 20 |
| `--num-essay-test` | Số mẫu câu hỏi tự luận cho test | 0 |
| `--num-mcqa-train` | Số mẫu câu hỏi trắc nghiệm cho training | 5 |
| `--num-mcqa-test` | Số mẫu câu hỏi trắc nghiệm cho test | 0 |
| `--model` / `-m` | Tên model LLM (ghi đè config) | Từ `llm_config.yaml` |
| `--base-url` | Endpoint API (ghi đè config) | Từ `llm_config.yaml` |

## Sinh dữ liệu DPO

Sử dụng script `src/generate_dpo_data.py`:

```bash
# Cơ bản - dùng model từ llm_config.yaml
python src/generate_dpo_data.py --input chunks.json --output ./dpo_output

# Tùy chỉnh số lượng mẫu và model
python src/generate_dpo_data.py \
    --input chunks.json \
    --output ./dpo_output \
    --num-samples 5 \
    --model gpt-4o-mini \
    --base-url https://api.openai.com/v1

# Resume từ lần chạy bị gián đoạn (chạy lại cùng lệnh)
python src/generate_dpo_data.py --input chunks.json --output ./dpo_output
```

### Tham số DPO

| Tham số | Mô tả | Giá trị mặc định |
|---------|-------|-----------------|
| `--input` / `-i` | Đường dẫn file input JSON/JSONL | **Bắt buộc** |
| `--output` / `-o` | Đường dẫn thư mục output (không phải file) | **Bắt buộc** |
| `--num-samples` | Số mẫu DPO cần sinh | 2 |
| `--model` / `-m` | Tên model LLM (ghi đè config) | Từ `llm_config.yaml` |
| `--base-url` | Endpoint API (ghi đè config) | Từ `llm_config.yaml` |
### Cấu trúc thư mục output sau khi chạy SFT

```
./sft_output/
├── keywords.json          # Kết quả bước 1
├── essay_questions.json   # Kết quả bước 2
├── essay_answers.json     # Kết quả bước 3
├── mcqa_questions.json    # Kết quả bước 4
├── mcqa_answers.json      # Kết quả bước 5
└── sft_data.json          # Kết quả cuối cùng
```

### Cấu trúc thư mục output sau khi chạy DPO

```
./dpo_output/
├── keywords.json          # Kết quả bước 1
├── essay_questions.json   # Kết quả bước 2
├── dpo_answers.json       # Kết quả bước 3
└── dpo_data.json          # Kết quả cuối cùng
```

## Cấu trúc dữ liệu output

### SFT output format

```json
[
  {
    "question": "Câu hỏi tự luận/trắc nghiệm...",
    "answer": "Câu trả lời...",
    "id": "unique_question_id",
    "question_type": "tuluan",
    "domain": "Lĩnh vực",
    "original_document": "chunk_id",
    "data_type": "train"
  }
]
```

### DPO output format

```json
[
  {
    "question": "Câu hỏi...",
    "accepted_answer": "Câu trả lời được chấp nhận (chất lượng cao)",
    "rejected_answer": "Câu trả lời bị từ chối (chất lượng thấp)",
    "id": "unique_question_id",
    "domain": "Lĩnh vực",
    "original_document": "chunk_id"
  }
]
```

## Chạy test

Các file test nằm trong `src/test/`:

```bash
# Test SFT
python -m src.test.test_sft_generation_service

# Test DPO
python -m src.test.test_dpo_generation_service
```

> **Lưu ý:** Các test này gọi API thực tế, cần cấu hình API key hợp lệ trong `settings/llm_config.yaml`.

## Kiến trúc thư mục

```
ViLLMPrep/
├── settings/
│   ├── llm_config.yaml           # Cấu hình LLM
│   └── service_config.yaml       # Cấu hình service
├── src/
│   ├── generate_utils.py         # Shared utilities (load chunks, save/load intermediate, resume)
│   ├── generate_sft_data.py      # CLI script sinh dữ liệu SFT (resumable pipeline)
│   ├── generate_dpo_data.py      # CLI script sinh dữ liệu DPO (resumable pipeline)
│   ├── app.py                    # FastAPI application
│   ├── configs/                  # Cấu hình và logging
│   ├── core/                     # Core logic (keyword extraction, QA generation, etc.)
│   ├── functions/                # Service functions (sft_generation_service, dpo_generation_service)
│   ├── schemas/                  # Pydantic models
│   └── test/                     # Unit tests
├── requirements.txt
└── README.md
