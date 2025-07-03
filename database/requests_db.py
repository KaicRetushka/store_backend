from sqlalchemy import select

from database.models import Session, UsersModel, CategoriesModel

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


async def check_admin(id):
    async with Session() as session:
        query = select(UsersModel).filter((UsersModel.id == id) & (UsersModel.role == "Admin"))
        admin = await session.execute(query)
        if admin.first():
            return True
        return False

async def insert_category(name):
    async with Session() as session:
        query = select(CategoriesModel).filter(CategoriesModel.name == name)
        category = await session.execute(query)
        if category.first():
            return False
        category = CategoriesModel(name=name)
        session.add(category)
        await session.commit()
        return category.id

async def select_categories():
    async with Session() as session:
        query = select(CategoriesModel)
        categories = await session.execute(query)
        categories = categories.scalars().all()
        categories_list = []
        for category in categories:
            categories_list.append({
                "id": category.id,
                "name": category.name
            })
        return categories_list

async def delete_category(id):
    async with Session() as session:
        query = select(CategoriesModel).filter(CategoriesModel.id == id)
        category = await session.execute(query)
        category = category.scalar_one_or_none()
        if not(category):
            return {"status_code": 410, "detail": "Такой категории и так не существует"}
        await session.delete(category)
        await session.commit()
        return {"status_code": 200, "detail": f"Категория с id {id} удалена"}

async def update_category(id, name):
    async with Session() as session:
        query = select(CategoriesModel).filter(CategoriesModel.id == id)
        category = await session.execute(query)
        category = category.scalar_one_or_none()
        if not (category):
            return {"status_code": 410, "detail": "Категории c таким id не существует"}
        query = select(CategoriesModel).filter((CategoriesModel.id != id) & (CategoriesModel.name == name))
        category2 = await session.execute(query)
        if category2.first():
            return {"status_code": 409, "detail": "Такая категория уже существует"}
        category.name = name
        await session.commit()
        return {"status_code": 200, "detail": "Категория изменена"}