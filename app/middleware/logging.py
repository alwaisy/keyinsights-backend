import time
import uuid
from fastapi import Request
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next):
    """
    Middleware to log request and response details
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Log request
    logger.info(f"Request {request_id} started: {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log response
    logger.info(f"Request {request_id} completed: {response.status_code} in {process_time:.4f}s")

    # Add custom headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)

    return response