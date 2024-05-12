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
    import random
    from datetime import datetime
    from apps.user import model as user_model
    await user_model.User.bulk_create(
        objects=[
            user_model.User(
                uid=f"test{idx}",
                social_type=random.choice(["kakao", "google"]),
                name=f"Test user {idx}",
            )
            for idx in range(1, 11)
        ]
    )

    await user_model.Follow.bulk_create(
        objects=[
            user_model.Follow(
                user_id=2,
                target_user_id=1,
                status="accepted",
            ),
            user_model.Follow(
                user_id=3,
                target_user_id=1,
            ),
            user_model.Follow(
                user_id=4,
                target_user_id=1,
            ),
            user_model.Follow(
                user_id=1,
                target_user_id=2,
                status="accepted",
            ),
            user_model.Follow(
                user_id=1,
                target_user_id=3,
                status="accepted",
            ),
            user_model.Follow(
                user_id=1,
                target_user_id=4,
            ),
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

    import apps.calendar.model as calendar_model
    await calendar_model.Calendar.create(name="Test Calendar 1")
    await calendar_model.CalendarUser.create(user_id=1, calendar_id=1)
