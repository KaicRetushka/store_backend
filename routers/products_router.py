from fastapi import APIRouter, Depends, Request, UploadFile, File, Form, HTTPException
from typing import List

from jwt_settings import security, config
from database.requests_db import (insert_product, select_products, select_product, update_product, delete_product,
                                  select_product_me)
from pydantic_classes import ProductInfoSchema, DetailReturnSchema

products_router = APIRouter(prefix="/api/products")

@products_router.get("/me", tags=["Товары (Products)"], dependencies=[Depends(security.access_token_required)])
async def give_products_me(request: Request):
    token = request.cookies[config.JWT_ACCESS_COOKIE_NAME]
    user_id = int(security._decode_token(token).sub)
    products_list = await select_product_me(user_id)
    return products_list

@products_router.get("/", tags=["Товары (Products)"])
async def give_products() -> List[ProductInfoSchema]:
    products_list = await select_products()
    return products_list

@products_router.get("/{id}", tags=["Товары (Products)"])
async def give_product(id: int) -> ProductInfoSchema:
    product_info = await select_product(id)
    if product_info:
        return product_info
    raise HTTPException(status_code=404, detail="Продукта с таким id не существует")

@products_router.post("/", tags=["Товары (Products)"],
                      dependencies=[Depends(security.access_token_required)])
async def add_product(request: Request, name: str = Form(...), price: float = Form(...),
                      description: str = Form(...), image: UploadFile = File(...),
                      category_id: int = Form(...)) -> ProductInfoSchema:
    image_bytes = await image.read()
    token = request.cookies[config.JWT_ACCESS_COOKIE_NAME]
    user_id = int(security._decode_token(token).sub)
    response = await insert_product(name, price, description, image_bytes, category_id, user_id)
    if response:
        return {"id": response["product_id"], "name": name, "price": price, "description": description,
                "image": response["image"], "category_id": category_id}
    raise HTTPException(status_code=404, detail="Неверный category_id")

@products_router.put("/{id}", tags=["Товары (Products)"], dependencies=[Depends(security.access_token_required)])
async def put_product(id: int, request: Request, name: str = Form(None), price: float = Form(None),
                      description: str = Form(None), image: UploadFile = File(None),
                      category_id: int = Form(None)) -> ProductInfoSchema:
    token = request.cookies[config.JWT_ACCESS_COOKIE_NAME]
    user_id = int(security._decode_token(token).sub)
    image_bytes = None
    if image:
        image_bytes = image.read()
    response_db = await update_product(name, price, description, image_bytes, category_id, user_id, id)
    if response_db["status_code"] != 200:
        raise HTTPException(status_code=response_db["status_code"], detail=response_db["detail"])
    return response_db["product_info"]

@products_router.delete("/{id}", tags=["Товары (Products)"],
                        dependencies=[Depends(security.access_token_required)])
async def drop_product(id: int, request: Request) -> DetailReturnSchema:
    token = request.cookies[config.JWT_ACCESS_COOKIE_NAME]
    user_id = int(security._decode_token(token).sub)
    response_db = await delete_product(id, user_id)
    if response_db:
        return {"detail": "Продукт удален"}
    else:
        raise HTTPException(status_code=404, detail="У вас нет продукта c таким id")