from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import text
import base64

from database.models import Session, UsersModel, CategoriesModel, ProductsModel, CartModel, OrdersModel

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
        await session.execute(text("PRAGMA foreign_keys = ON"))
        query = select(CategoriesModel).filter(CategoriesModel.id == id)
        category = await session.execute(query)
        category = category.scalar_one_or_none()
        if not(category):
            return {"status_code": 410, "detail": "Такой категории и так не существует"}
        try:
            await session.delete(category)
            await session.commit()
            return {"status_code": 200, "detail": f"Категория с id {id} удалена"}
        except IntegrityError:
            return {"status_code": 409, "detail": "Товары с таккой категорией существуют"}


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

async def insert_product(name, price, description, image_bytes, category_id, user_id):
    async with Session() as session:
        await session.execute(text("PRAGMA foreign_keys = ON"))
        query = select(CategoriesModel).filter(CategoriesModel.id == category_id)
        category = await session.execute(query)
        if not(category.first()):
            return False
        image = base64.b64encode(image_bytes).decode("utf-8")
        product = ProductsModel(name=name, price=price, description=description, image=image, category_id=category_id,
                                salesman_id=user_id)
        session.add(product)
        await session.commit()
        return {"product_id": product.id, "image": image}

async def select_products():
    async with Session() as session:
        query = select(ProductsModel)
        products = await session.execute(query)
        products = products.scalars().all()
        products_list = []
        for product in products:
            products_list.append({"id": product.id, "name": product.name, "price": product.price,
                                  "description": product.description, "image": product.image,
                                  "category_id": product.category_id})
        return products_list

async def select_product(id):
    async with Session() as session:
        query = select(ProductsModel).filter(ProductsModel.id == id)
        product = await session.execute(query)
        product = product.scalars().first()
        if product:
            return {"id": product.id, "name": product.name, "price": product.price, "description": product.description,
                    "image": product.image, "category_id": product.category_id}
        return False

async def update_product(name, price, description, image_bytes, category_id, user_id, product_id):
    async with Session() as session:
        is_admin = await check_admin(user_id)
        if is_admin:
            query = select(ProductsModel).filter(ProductsModel.id == product_id)
        else:
            query = select(ProductsModel).filter((ProductsModel.id == product_id) &
                                                 (ProductsModel.salesman_id == user_id))
        product = await session.execute(query)
        product = product.scalars().first()
        if not product:
            return {"status_code": 409, "detail": "У вас нет продукта с таким id нет"}
        product.name = name or product.name
        product.price = price or product.price
        product.description = description or product.description
        if image_bytes:
            image = base64.b64encode(image_bytes).decode("utf-8")
            product.image = image
        query = select(CategoriesModel).filter(CategoriesModel.id == category_id)
        if category_id:
            category = await session.execute(query)
            if not category.first():
                return {"status_code": 409, "detail": "Категории стаким id нет"}
            product.category_id = category_id
        await session.commit()
        return {"status_code": 200, "product_info": {"id": product.id, "name": product.name, "price": product.price,
                                                     "description": product.description, "image": product.image,
                                                     "category_id": product.category_id}}

async def delete_product(product_id, user_id):
    async with Session() as session:
        await session.execute(text("PRAGMA foreign_keys = ON"))
        is_admin = await check_admin(user_id)
        if is_admin:
            query = select(ProductsModel).filter(ProductsModel.id == product_id)
        else:
            query = select(ProductsModel).filter((ProductsModel.id == product_id) & (ProductsModel.salesman_id == user_id))
        product = await session.execute(query)
        product = product.scalars().first()
        if not product:
            return False
        await session.delete(product)
        await session.commit()
        return True

async def select_product_me(user_id):
    async with Session() as session:
        query = select(ProductsModel).filter(ProductsModel.salesman_id == user_id)
        products = await session.execute(query)
        products = products.scalars().all()
        products_list = []
        for product in products:
            products_list.append({"id": product.id, "name": product.name, "price": product.price,
                                  "description": product.description, "image": product.image,
                                  "category_id": product.category_id})
        return products_list

async  def insert_product_in_cart(product_id, quantity, user_id):
    async with Session() as session:
        await session.execute(text("PRAGMA foreign_keys = ON"))
        query = select(ProductsModel).filter(ProductsModel.id == product_id)
        product = await session.execute(query)
        product = product.scalar_one_or_none()
        if not product:
            return False
        query = select(CartModel).filter((CartModel.product_id == product_id) & (CartModel.user_id == user_id))
        cart = await session.execute(query)
        cart = cart.scalar_one_or_none()
        if cart:
            cart.quantity = cart.quantity + quantity
            cart.price = cart.price * cart.quantity
            await session.commit()
            return True
        cart = CartModel(product_id=product_id, quantity=quantity, user_id=user_id, price=product.price * quantity)
        session.add(cart)
        await session.commit()
        return True

async def select_cart(user_id):
    async with Session() as session:
        query = select(CartModel).filter(CartModel.user_id == user_id)
        products = await session.execute(query)
        products = products.scalars().all()
        full_price = 0
        products_list = []
        for product in products:
            products_list.append({
                "product_id": product.product_id,
                "quantity": product.quantity,
                "price": product.price
            })
            full_price += product.price
        return {
            "full_price": full_price,
            "products_list": products_list
        }

async def update_product_in_cart(product_id, user_id, quantity):
    async with Session() as session:
        query = select(CartModel).filter((CartModel.product_id == product_id) & (CartModel.user_id == user_id))
        product_in_cart = await session.execute(query)
        product_in_cart = product_in_cart.scalar_one_or_none()
        if not product_in_cart:
            return False
        product_in_cart.quantity = quantity
        query = select(ProductsModel).filter(ProductsModel.id == product_id)
        product = await session.execute(query)
        product = product.scalar_one()
        product_in_cart.price = quantity * product.price
        await session.commit()
        return True

async def delete_product_in_cart(product_id, user_id):
    async with Session() as session:
        query = select(CartModel).filter((CartModel.product_id == product_id) & (CartModel.user_id == user_id))
        product_in_cart = await session.execute(query)
        product_in_cart = product_in_cart.scalar_one_or_none()
        if not product_in_cart:
            return False
        await session.delete(product_in_cart)
        await session.commit()
        return True

async def move_to_order(user_id):
    async with Session() as session:
        query = select(CartModel).filter(CartModel.user_id == user_id)
        products_in_cart = await session.execute(query)
        products_in_cart = products_in_cart.scalars().all()
        if len(products_in_cart) == 0:
            return False
        products_list = []
        full_price = 0
        for product_in_cart in products_in_cart:
            full_price += product_in_cart.price
            query = select(ProductsModel).filter(ProductsModel.id == product_in_cart.product_id)
            product = await session.execute(query)
            product = product.scalar_one()
            query = select(CategoriesModel).filter(CategoriesModel.id == product.category_id)
            category = await session.execute(query)
            category = category.scalar_one()
            products_list.append({
                "name": product.name,
                "description": product.description,
                "image": product.image,
                "price":  product.price,
                "category": category.name,
                "price_all": product_in_cart.price,
                "quantity": product_in_cart.quantity,
            })
            await session.delete(product_in_cart)
        order = OrdersModel(products_list=products_list, full_price=full_price, status="Создан", user_id=user_id)
        session.add(order)
        await session.commit()
        return True

async def select_me_orders(user_id):
    async with Session() as session:
        query = select(OrdersModel).filter(OrdersModel.user_id == user_id)
        orders = await session.execute(query)
        orders = orders.scalars().all()
        orders_list = []
        for order in orders:
            orders_list.append({
                "id": order.id,
                "full_price": order.full_price,
                "status": order.status,
                "products_list": order.products_list
            })
        return orders_list

async def select_orders():
    async with Session() as session:
        query = select(OrdersModel)
        orders = await session.execute(query)
        orders = orders.scalars().all()
        orders_list = []
        for order in orders:
            orders_list.append({
                "id": order.id,
                "full_price": order.full_price,
                "status": order.status,
                "products_list": order.products_list
            })
        return orders_list

async def select_order_id(id, user_id):
    async with Session() as session:
        is_admin = check_admin(user_id)
        if is_admin:
            query = select(OrdersModel).filter(OrdersModel.id == id)
        else:
            query = select(OrdersModel).filter((OrdersModel.id == id) & (OrdersModel.user_id == user_id))
        order = await session.execute(query)
        order = order.scalar_one_or_none()
        if not order:
            return False
        return {"id": order.id,
                "full_price": order.full_price,
                "status": order.status,
                "products_list": order.products_list
            }

async def update_status(id, status):
    async with Session() as session:
        query = select(OrdersModel).filter(OrdersModel.id == id)
        order = await session.execute(query)
        order = order.scalar_one_or_none()
        if not order:
            return False
        order.status = status
        await session.commit()
        return {"id": order.id,
                "full_price": order.full_price,
                "status": order.status,
                "products_list": order.products_list
            }