# import sys
# import os

# # Ensure the parent directory is in sys.path
# sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from test_app.middlewares import RequestLoggingMiddleware, ResponseTransformMiddleware
from test_app.routers import auth
from test_app.routers import user
import uvicorn
from test_app.database import create_tables

app = FastAPI(
    title="Advanced FastAPI Application",
    description="A production-ready FastAPI application with advanced features",
    version="1.0.0",

)
@app.on_event("startup")
async def on_startup():
    await create_tables()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourfrontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ResponseTransformMiddleware)


app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/user", tags=["User"])


@app.get("/")
def health_check():
    return {"status": "healthy"}
if __name__ == "__main__":
    
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)