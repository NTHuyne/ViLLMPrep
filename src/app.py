from typing import Optional, List
import logging

from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Header,
    status,
)
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager

from src.configs.config import settings
from src.schemas.schemas import (
    DPOGenerationRequest,
    SFTGenerationRequest,
    ResponseDPOItem,
    ResponseSFTItem,
)
from src.functions.dpo_generation_service import generate_dpo_data
from src.functions.sft_generation_service import generate_sft_data


logger = logging.getLogger("app")


async def verify_key(api_key: Optional[str] = Header(None)):
    """
    Verify API key.
    """
    if not api_key or api_key not in settings.API_KEYS:
        raise HTTPException(
            status_code=401,
            detail={
                "code": 401,
                "status": "error",
                "data": None,
                "message": "api-key is invalid!"
            }
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle.
    """
    logger.info("Starting the app...")
    yield
    logger.warning("Shutting down the app...")


app = FastAPI(
    root_path=settings.ROOT_PATH,
    lifespan=lifespan,
    title="AutoGen - Data Generation API",
    description="API for generating DPO and SFT data.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    """
    Handle HTTP exceptions.
    """
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(exc.detail),
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            {
                "code": 0,
                "message": f"Lỗi không xác định: {str(exc)}",
            }
        ),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    Handle request validation errors.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "detail": exc.errors(),
                "body": exc.body,
            }
        ),
    )


@app.get("/", tags=["Health Check"])
@app.get("/healthz", tags=["Health Check"])
async def get_healthz():
    """
    Health check endpoint.
    """
    return {"status": "ok"}


@app.post(
    "/generate_dpo",
    tags=["Data Generation"],
    response_model=List[ResponseDPOItem],
    dependencies=[Depends(verify_key)],
)
async def generate_dpo(request: DPOGenerationRequest):
    """
    Generate DPO dataset and return directly.
    """
    try:
        dpo_data = await generate_dpo_data(request)

        logger.info(
            f"Generated {len(dpo_data)} DPO samples successfully"
        )

        return dpo_data

    except Exception as e:
        logger.exception("Error generating DPO data")

        raise HTTPException(
            status_code=500,
            detail={
                "code": 1,
                "message": str(e),
            },
        )


@app.post(
    "/generate_sft",
    tags=["Data Generation"],
    response_model=List[ResponseSFTItem],
    dependencies=[Depends(verify_key)],
)
async def generate_sft(request: SFTGenerationRequest):
    """
    Generate SFT dataset and return directly.
    """
    try:
        sft_data = await generate_sft_data(request)

        logger.info(
            f"Generated {len(sft_data)} SFT samples successfully"
        )

        return sft_data

    except Exception as e:
        logger.exception("Error generating SFT data")

        raise HTTPException(
            status_code=500,
            detail={
                "code": 1,
                "message": str(e),
            },
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8044,
        reload=False,
    )