from typing import Optional

from pydantic import BaseModel, EmailStr

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