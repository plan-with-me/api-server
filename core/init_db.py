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
    from datetime import datetime
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
            user_model.User(
                uid="3463192767", # 경천님
                social_type="kakao",
                name="스트릿출신 순두부",
            )
        ]
    )

    from apps.goal import model as goal_model
    await goal_model.TopGoal.create(
        name="Test topgoal 1",
        user_id=1
    )
    await goal_model.TopGoal.create(
        name="Test topgoal 2",
        user_id=2
    )
    for idx in range(1, 11):
        await goal_model.TopGoal.create(
            name=f"테스트 상위목표 {idx}",
            user_id=3,
        )

    await goal_model.SubGoal.create(
        name="Test subgoal1",
        plan_datetime=datetime(2024, 12, 30),
        user_id=1,
        top_goal_id=1,
    )
    await goal_model.SubGoal.create(
        name="Test subgoal2",
        plan_datetime=datetime(2024, 12, 30),
        user_id=2,
        top_goal_id=2,
    )
