from fastapi import APIRouter, Depends, Request, HTTPException
from typing import List

from jwt_settings import security, config
from pydantic_classes import CategoryAddSchema, CategoryInfoSchema, DetailReturnSchema
from database.requests_db import check_admin, insert_category, select_categories, delete_category, update_category

categories_router = APIRouter(prefix="/api/categories")

@categories_router.get("/", tags=["Категории (Categories)"])
async def get_categories() -> List[CategoryInfoSchema]:
    categories_list = await select_categories()
    return categories_list

@categories_router.post("/", tags=["Категории (Categories)"],
                        dependencies=[Depends(security.access_token_required)])
async def post_categories(body: CategoryAddSchema, request: Request) -> CategoryInfoSchema:
    token = request.cookies[config.JWT_ACCESS_COOKIE_NAME]
    user_id = int(security._decode_token(token).sub)
    is_admin = await check_admin(user_id)
    if not(is_admin):
        raise HTTPException(status_code=403, detail="Вы не являетесь администратором")
    category_id = await insert_category(body.name)
    if not(category_id):
        raise HTTPException(status_code=409, detail="Такая категория уже существует")
    return {"id": category_id, "name": body.name}

@categories_router.put("/{", tags=["Категории (Categories)"],
                        dependencies=[Depends(security.access_token_required)])
async def put_categories(body: CategoryInfoSchema, request: Request) -> DetailReturnSchema:
    token = request.cookies[config.JWT_ACCESS_COOKIE_NAME]
    user_id = int(security._decode_token(token).sub)
    is_admin = await check_admin(user_id)
    if not(is_admin):
        raise HTTPException(status_code=403, detail="Вы не являетесь администратором")
    response_db = await update_category(body.id, body.name)
    if response_db["status_code"] != 200:
        raise HTTPException(status_code=response_db["status_code"], detail=response_db["detail"])
    return {"detail": response_db["detail"]}

@categories_router.delete("/{id}", tags=["Категории (Categories)"],
                        dependencies=[Depends(security.access_token_required)])
async def delete_categories(id: int, request: Request) -> DetailReturnSchema:
    token = request.cookies[config.JWT_ACCESS_COOKIE_NAME]
    user_id = int(security._decode_token(token).sub)
    is_admin = await check_admin(user_id)
    if not (is_admin):
        raise HTTPException(status_code=403, detail="Вы не являетесь администратором")
    response_db = await delete_category(id)
    if response_db["status_code"] == 410:
        raise HTTPException(status_code=response_db["status_code"], detail=response_db["detail"])
    return {"detail": response_db["detail"]}