from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_async_engine("sqlite+aiosqlite:///mydb.db")

Session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

class UsersModel(Base):
    __tablename__ = "users"
    email: Mapped[str]
    password: Mapped[str]
    name: Mapped[str]
    role: Mapped[str]

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)