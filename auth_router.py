from fastapi import APIRouter, HTTPException, Response, Depends, Request

from  pydantic_classes import UserLoginSchema, UserAddSchema, TokenReturnSchema, UserInfoReturnSchema, UserChangeSchema
from requests_db import insert_user, check_user, select_user, update_user
from jwt_settings import config, security

auth_router = APIRouter(prefix="/api/auth")

@auth_router.post("/register", tags=["Пользователи (Auth & Users)"])
async def register(body: UserAddSchema, response: Response) -> TokenReturnSchema:
    response_db = await insert_user(body.email, body.password, body.name)
    if response_db:
        token = security.create_access_token(uid=str(response_db))
        response.set_cookie(key=config.JWT_ACCESS_COOKIE_NAME,
                            value=token,
                            httponly=True,
                            samesite="lax",
                            secure=False)
        return {"token": token}
    raise HTTPException(status_code=409, detail="Такая почта уже занята")

@auth_router.post("/login", tags=["Пользователи (Auth & Users)"])
async def login(body: UserLoginSchema, response: Response) -> TokenReturnSchema:
    response_db = await check_user(body.email, body.password)
    if response_db:
        token = security.create_access_token(uid=str(response_db))
        response.set_cookie(key=config.JWT_ACCESS_COOKIE_NAME,
                            value=token,
                            httponly=True,
                            samesite="lax",
                            secure=False)
        return {"token": token}
    raise HTTPException(status_code=404, detail="Неверная почта или пароль")

@auth_router.get("/me", tags=["Пользователи (Auth & Users)"],
                 dependencies=[Depends(security.access_token_required)])
async def get_me(request: Request) -> UserInfoReturnSchema:
    token = request.cookies[config.JWT_ACCESS_COOKIE_NAME]
    user_id = int(security._decode_token(token).sub)
    user_info = await select_user(user_id)
    return user_info

@auth_router.put("/me", tags=["Пользователи (Auth & Users)"],
                 dependencies=[Depends(security.access_token_required)])
async def put_me(body: UserChangeSchema, request: Request) -> UserInfoReturnSchema:
    token = request.cookies[config.JWT_ACCESS_COOKIE_NAME]
    user_id = int(security._decode_token(token).sub)
    user_info = await update_user(user_id, body.email, body.name)
    if user_info:
        return user_info
    raise HTTPException(status_code=409, detail="Такая почта уже занята")