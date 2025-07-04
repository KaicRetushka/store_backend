from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import PositiveInt

from jwt_settings import config, security
from pydantic_classes import AddProductInCartSchema, ReturnCartSchema, PutProductInCartSchema
from database.requests_db import insert_product_in_cart, select_cart, update_product_in_cart, delete_product_in_cart

cart_router = APIRouter(prefix="/api/cart")

@cart_router.get("/", tags=["Корзина (Cart)"], dependencies=[Depends(security.access_token_required)])
async def give_cart(request: Request) -> ReturnCartSchema:
    token = request.cookies[config.JWT_ACCESS_COOKIE_NAME]
    user_id = int(security._decode_token(token).sub)
    response_db = await select_cart(user_id)
    return response_db

@cart_router.post("/add", tags=["Корзина (Cart)"], dependencies=[Depends(security.access_token_required)])
async def add_product_in_cart(body: AddProductInCartSchema, request: Request) -> ReturnCartSchema:
    token = request.cookies[config.JWT_ACCESS_COOKIE_NAME]
    user_id = int(security._decode_token(token).sub)
    response_db = await insert_product_in_cart(body.product_id, body.quantity, user_id)
    if response_db:
        response_db = await select_cart(user_id)
        return response_db
    raise HTTPException(status_code=404, detail="Нет товара с таким id")

@cart_router.put("/update/{product_id}", tags=["Корзина (Cart)"],
                 dependencies=[Depends(security.access_token_required)])
async def put_product_in_cart(body: PutProductInCartSchema, product_id: int, request: Request) -> ReturnCartSchema:
    token = request.cookies[config.JWT_ACCESS_COOKIE_NAME]
    user_id = int(security._decode_token(token).sub)
    response_db = await update_product_in_cart(product_id, user_id, body.quantity)
    if not response_db:
        raise HTTPException(status_code=404, detail="У вас в корзине нет товара с таким id")
    response_db = await select_cart(user_id)
    return response_db

@cart_router.delete("/remove/{product_id}", tags=["Корзина (Cart)"],
                    dependencies=[Depends(security.access_token_required)])
async def remove_product_in_cart(product_id: PositiveInt, request: Request) -> ReturnCartSchema:
    token = request.cookies[config.JWT_ACCESS_COOKIE_NAME]
    user_id = int(security._decode_token(token).sub)
    response_db = await delete_product_in_cart(product_id, user_id)
    if not response_db:
        raise HTTPException(status_code=410, detail="У вас в корзине нет товара с таким id")
    response_db = await select_cart(user_id)
    return response_db