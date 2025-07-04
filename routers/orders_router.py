from fastapi import APIRouter, Request, Depends, HTTPException
from typing import List

from jwt_settings import security, config
from pydantic_classes import OrderInfoSchema, ChangeStatusSchema
from database.requests_db import select_me_orders, check_admin, select_orders, select_order_id, update_status

orders_router = APIRouter(prefix="/api/orders")

@orders_router.get("/", tags=["Заказы (Orders)"], dependencies=[Depends(security.access_token_required)],
                   description="Возращает все заказы пользователя")
async def give_orders(request: Request) -> List[OrderInfoSchema]:
    token = request.cookies[config.JWT_ACCESS_COOKIE_NAME]
    user_id = int(security._decode_token(token).sub)
    response_db = await select_me_orders(user_id)
    return response_db

@orders_router.get("/admin", tags=["Заказы (Orders)"], dependencies=[Depends(security.access_token_required)],
                   description="Возращает абсолютно все заказы, доступно только админу")
async def give_all_oders(request: Request) -> List[OrderInfoSchema]:
    token = request.cookies[config.JWT_ACCESS_COOKIE_NAME]
    user_id = int(security._decode_token(token).sub)
    is_admin = await check_admin(user_id)
    if not(is_admin):
        raise HTTPException(status_code=403, detail="Вы не являетесь администратором")
    response_db = await select_orders()
    return response_db

@orders_router.get("/{id}", tags=["Заказы (Orders)"], dependencies=[Depends(security.access_token_required)],
                   description="Возращает заказ по id")
async def give_order_id(id: int, request: Request) -> OrderInfoSchema:
    token = request.cookies[config.JWT_ACCESS_COOKIE_NAME]
    user_id = int(security._decode_token(token).sub)
    response_db = await select_order_id(id, user_id)
    if not response_db:
        raise HTTPException(status_code=404, detail="Заказа с таким id не существует")
    return response_db

@orders_router.put("/{id}/status", tags=["Заказы (Orders)"],
                   dependencies=[Depends(security.access_token_required)],
                   description="Изменяет статус заказа, доступно только админу")
async def change_status(id: int, body: ChangeStatusSchema, request: Request) -> OrderInfoSchema:
    token = request.cookies[config.JWT_ACCESS_COOKIE_NAME]
    user_id = int(security._decode_token(token).sub)
    is_admin = await check_admin(user_id)
    if not(is_admin):
        raise HTTPException(status_code=403, detail="Вы не являетесь администратором")
    response_db = await update_status(id, body.status)
    if not response_db:
        raise HTTPException(status_code=404, detail="Не существует заказа с таким id")
    return response_db