from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from authx.exceptions import MissingTokenError, JWTDecodeError
import uvicorn
import asyncio

from routers.auth_router import auth_router
from routers.categories_router import categories_router
from database.models import create_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
    allow_origins=["*"]
)

app.include_router(router=auth_router)
app.include_router(router=categories_router)

@app.exception_handler(MissingTokenError)
async def missing_token(request, exc):
    raise HTTPException(status_code=403, detail="Вы не зарегисрированы")

@app.exception_handler(JWTDecodeError)
async def jwt_decode_error(request, exc):
    raise HTTPException(status_code=403, detail="Токен истек")


if __name__ == "__main__":
    asyncio.run(create_db())
    uvicorn.run("main:app", reload=True)