from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select, LargeBinary, ForeignKey



engine = create_async_engine("sqlite+aiosqlite:///database/mydb.db")

Session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

class UsersModel(Base):
    __tablename__ = "users"
    email: Mapped[str]
    password: Mapped[str]
    name: Mapped[str]
    role: Mapped[str]

class CategoriesModel(Base):
    __tablename__ = "categories"
    name: Mapped[str]

class ProductsModel(Base):
    __tablename__ = "products"
    name: Mapped[str]
    price: Mapped[float]
    description: Mapped[str]
    image: Mapped[str]
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    salesman_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

async def create_db():
    async with engine.begin() as conn:
        # await conn.execute(text("PRAGMA foreign_keys = ON"))
        await conn.run_sync(Base.metadata.create_all)
    async with Session() as session:
        query = select(UsersModel).filter(UsersModel.role == "Admin")
        admin = await session.execute(query)
        if not(admin.first()):
            admin = UsersModel(email="admin@gmail.com", password="admin", name="Администратор", role="Admin")
            session.add(admin)
            await session.commit()