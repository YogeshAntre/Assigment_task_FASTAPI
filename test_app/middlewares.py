from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
import uuid

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        
        # Log request details
        logging.info(f"Request ID: {request_id}")
        logging.info(f"Method: {request.method}")
        logging.info(f"URL: {request.url}")
        
        
        headers = dict(request.headers)
        logging.info(f"Headers: {headers}")
        
        # Track request processing time
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        logging.info(f"Request processed yoga in {process_time:.4f} seconds")
        
        # Add custom headers to response
        response.headers['X-Request-ID'] = request_id
        response.headers['X-Process-Time'] = str(process_time)
        
        return response

class ResponseTransformMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        

        if response.status_code == 200:

            pass
        
        return response
