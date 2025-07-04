from typing import Optional, List

from pydantic import BaseModel, EmailStr, PositiveInt, Field


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class UserAddSchema(UserLoginSchema):
    name: str

class TokenReturnSchema(BaseModel):
    token: str

class UserInfoReturnSchema(BaseModel):
    id: int
    email: str
    name: str
    role: str

class UserChangeSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class CategoryAddSchema(BaseModel):
    name: str

class CategoryInfoSchema(BaseModel):
    id: int
    name: str

class DetailReturnSchema(BaseModel):
    detail: str

class ProductInfoSchema(BaseModel):
    id: int
    name: str
    price: float
    description: str
    image: str
    category_id: int

class AddProductInCartSchema(BaseModel):
    product_id: int
    quantity: PositiveInt

class ProductInCartSchema(BaseModel):
    product_id: int
    quantity: PositiveInt
    price: float

class ReturnCartSchema(BaseModel):
    full_price: float
    products_list: List[ProductInCartSchema]

class PutProductInCartSchema(BaseModel):
    quantity: PositiveInt