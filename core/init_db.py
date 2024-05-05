from tortoise import Tortoise

from core.config import secrets


async def schema_and_tables(safe: bool=True):
    default_db_conn = Tortoise.get_connection("default")
    if not safe:
        try: 
            await default_db_conn.execute_query(f"DROP SCHEMA {secrets.DB_SCHEMA} CASCADE")
            await default_db_conn.execute_query(f"CREATE SCHEMA {secrets.DB_SCHEMA}")
        except:
            await default_db_conn.execute_query(f"CREATE SCHEMA {secrets.DB_SCHEMA}")
    await Tortoise.generate_schemas(safe=safe)


async def dummy_data():
    from apps.user import model as user_model

    await user_model.User.bulk_create(
        objects=[
            user_model.User(
                uid="test1",
                social_type="kakao",
                name="Test user 1",
            ),
            user_model.User(
                uid="test2",
                social_type="google",
                name="Test user 2",
            ),
        ]
    )
