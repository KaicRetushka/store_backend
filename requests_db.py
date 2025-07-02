from dns.e164 import query
from sqlalchemy import select

from  models import Session, UsersModel

async def insert_user(email, password, name):
    async with Session() as session:
        query = select(UsersModel).filter(UsersModel.email == email)
        user = await session.execute(query)
        if user.first():
            return False
        user = UsersModel(email=email, password=password, name=name, role="User")
        session.add(user)
        await session.commit()
        return user.id

async def check_user(email, password):
    async with Session() as session:
        query = select(UsersModel).filter((UsersModel.email == email) & (UsersModel.password == password))
        user = await session.execute(query)
        user = user.scalars().first()
        if user:
            return user.id
        return False

async def select_user(id):
    async with Session() as session:
        query = select(UsersModel).filter(UsersModel.id == id)
        user = await session.execute(query)
        user = user.scalars().first()
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }

async def update_user(id, email, name):
    async with Session() as session:
        query = select(UsersModel).filter((UsersModel.id != id) & (UsersModel.email == email))
        response = await session.execute(query)
        if response.first():
            return False
        query = select(UsersModel).filter(UsersModel.id == id)
        user = await session.execute(query)
        user = user.scalars().first()
        user.email = email
        user.name = name
        await session.commit()
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
