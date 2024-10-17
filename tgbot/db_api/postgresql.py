from typing import Union

import asyncpg
from asyncpg import Pool, Connection

from tgbot.config import load_config

config = load_config(".env")


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.db.user,
            password=config.db.password,
            host=config.db.host,
            database=config.db.database,
            max_inactive_connection_lifetime=3
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):

        async with self.pool.acquire() as connection:
            connection: Connection()
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Arial_users (
        id SERIAL PRIMARY KEY,
        brand VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        username VARCHAR(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE,
        number BIGINT NOT NULL,
        language VARCHAR(255) NOT NULL
        );
        """
        await self.execute(sql, fetch=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    @staticmethod
    def format_args2(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=2)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, brand, name, username, telegram_id, number, language):
        sql = "INSERT INTO Arial_users (brand, name, username, telegram_id, number, language) " \
              "VALUES($1, $2, $3, $4, $5, $6) returning *"
        return await self.execute(sql, brand, name, username, telegram_id, number, language, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Arial_users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Arial_users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def update_user(self, telegram_id, **kwargs):
        sql = "UPDATE Arial_users SET "
        sql, parameters = self.format_args2(sql, parameters=kwargs)
        sql += f"WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, *parameters, execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Arial_users", execute=True)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    async def create_table_admins(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Arial_Admins (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT NOT NULL UNIQUE, 
        name VARCHAR(255) NOT NULL
        );
        """
        await self.execute(sql, fetch=True)

    async def add_administrator(self, telegram_id, name):
        sql = "INSERT INTO Arial_Admins (telegram_id, name) VALUES ($1, $2) returning *"
        return await self.execute(sql, telegram_id, name, fetchrow=True)

    async def select_all_admins(self):
        sql = "SELECT * FROM Arial_Admins"
        return await self.execute(sql, fetch=True)

    async def select_id_admins(self):
        sql = "SELECT telegram_id FROM Arial_Admins"
        return await self.execute(sql, fetch=True)

    async def select_admin(self, **kwargs):
        sql = "SELECT * FROM Arial_Admins WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def delete_admin(self, telegram_id):
        await self.execute("DELETE FROM Arial_Admins WHERE telegram_id=$1", telegram_id, execute=True)

    async def drop_admins(self):
        await self.execute("DROP TABLE Arial_Admins", execute=True)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    async def create_table_products(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Flayers (
        id SERIAL PRIMARY KEY,
        category VARCHAR(255) NOT NULL,
        sub1category VARCHAR(255) NOT NULL,
        sub1category_uz VARCHAR(255) NOT NULL,
        photos TEXT NOT NULL, 
        name VARCHAR(255) NOT NULL,
        name_uz VARCHAR(255) NOT NULL
        );
        """
        await self.execute(sql, fetch=True)

    async def add_product(self, category, sub1category, sub1category_uz, photos, name, name_uz):
        sql = "INSERT INTO Flayers (category, sub1category, sub1category_uz, photos, name, name_uz) " \
              "VALUES($1, $2, $3, $4, $5, $6) returning *"
        return await self.execute(sql, category, sub1category, sub1category_uz, photos, name, name_uz, fetchrow=True)

    async def drop_products(self):
        await self.execute("DROP TABLE Flayers", execute=True)

    async def select_in_category(self, category):
        sql = "SELECT * FROM Flayers WHERE category=$1"
        return await self.execute(sql, category, fetch=True)

    async def select_in_sub1category(self, category, sub1category):
        sql = "SELECT * FROM Flayers WHERE category=$1 AND sub1category=$2"
        return await self.execute(sql, category, sub1category, fetch=True)

    async def select_in_sub1category_uz(self, category, sub1category_uz):
        sql = "SELECT * FROM Flayers WHERE category=$1 AND sub1category_uz=$2"
        return await self.execute(sql, category, sub1category_uz, fetch=True)

    async def select_in_sub2category(self, category, sub1category, sub2category):
        sql = "SELECT * FROM Flayers WHERE category=$1 AND sub1category=$2 AND sub2category=$3"
        return await self.execute(sql, category, sub1category, sub2category, fetch=True)

    async def select_in_sub2category_uz(self, category, sub1category_uz, sub2category_uz):
        sql = "SELECT * FROM Flayers WHERE category=$1 AND sub1category_uz=$2 AND sub2category_uz=$3"
        return await self.execute(sql, category, sub1category_uz, sub2category_uz, fetch=True)

    async def select_product(self, **kwargs):
        sql = "SELECT * FROM Flayers WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_product_in_sub1category(self, category, sub1category, name):
        sql = "SELECT * FROM Flayers WHERE category=$1 AND sub1category=$2 AND name=$3"
        return await self.execute(sql, category, sub1category, name, fetchrow=True)

    async def select_product_in_sub1category_uz(self, category, sub1category, name_uz):
        sql = "SELECT * FROM Flayers WHERE category=$1 AND sub1category=$2 AND name_uz=$3"
        return await self.execute(sql, category, sub1category, name_uz, fetchrow=True)

    async def update_product(self, id, **kwargs):
        sql = "UPDATE Flayers SET "
        sql, parameters = self.format_args2(sql, parameters=kwargs)
        sql += f"WHERE id=$1"
        return await self.execute(sql, id, *parameters, execute=True)

    async def select_all_products(self):
        sql = "SELECT * FROM Flayers"
        return await self.execute(sql, fetch=True)

    async def delete_product(self, id):
        await self.execute("DELETE FROM Flayers WHERE id=$1", id, execute=True)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    async def create_table_cart(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Arial_Cart (
        id SERIAL PRIMARY KEY,
        flayer_id INTEGER NOT NULL,
        buyer BIGINT NOT NULL
        );
        """
        await self.execute(sql, fetch=True)

    async def add_to_cart(self, flayer_id, buyer):
        sql = "INSERT INTO Arial_Cart (flayer_id, buyer) VALUES($1, $2) returning *"
        return await self.execute(sql, flayer_id, buyer, fetchrow=True)

    async def drop_cart(self):
        await self.execute("DROP TABLE Arial_Cart", execute=True)

    async def select_in_cart(self, **kwargs):
        sql = "SELECT * FROM Arial_Cart WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_cart(self, buyer):
        sql = "SELECT * FROM Arial_Cart WHERE buyer=$1"
        return await self.execute(sql, buyer, fetch=True)

    async def delete_flayer_id_cart(self, buyer, flayer_id):
        sql = "DELETE FROM Arial_Cart WHERE buyer=$1 AND flayer_id=$2"
        return await self.execute(sql, buyer, flayer_id, execute=True)

    async def update_cart(self, quantity, **kwargs):
        sql = "UPDATE Arial_Cart SET quantity=$1 WHERE "
        sql, parameters = self.format_args2(sql, parameters=kwargs)
        return await self.execute(sql, quantity, *parameters, execute=True)

    async def count_in_cart(self, buyer):
        sql = "SELECT COUNT(*) FROM Arial_Cart WHERE buyer=$1"
        return await self.execute(sql, buyer, fetchval=True)

    async def delete_in_cart(self, flayer_id):
        await self.execute("DELETE FROM Arial_Cart WHERE flayer_id=$1", flayer_id, execute=True)

    async def delete_cart(self, buyer):
        await self.execute("DELETE FROM Arial_Cart WHERE buyer=$1", buyer, execute=True)

