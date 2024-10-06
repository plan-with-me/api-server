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

    await default_db_conn.execute_query("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    await default_db_conn.execute_query("DROP FUNCTION IF EXISTS decompose_korean;")
    await default_db_conn.execute_query("""
        CREATE OR REPLACE FUNCTION decompose_korean(input_text TEXT)
        RETURNS TEXT AS $$
        DECLARE
            result TEXT := '';
            ch TEXT;
            uni_val INT;
            cho INT;
            jung INT;
            jong INT;
            chosung TEXT[] := ARRAY['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'];
            jungsung TEXT[] := ARRAY['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ'];
            jongsung TEXT[] := ARRAY['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'];
        BEGIN
            FOR i IN 1..LENGTH(input_text) LOOP
                -- 한 글자씩 추출
                ch := SUBSTRING(input_text, i, 1);
                uni_val := ASCII(ch);

                -- 유니코드 값이 한글 범위에 있는지 확인
                IF uni_val BETWEEN 44032 AND 55203 THEN
                    -- 한글 자모 분리
                    uni_val := uni_val - 44032;
                    cho := uni_val / 588;
                    jung := (uni_val % 588) / 28;
                    jong := uni_val % 28;
                    -- 결과 문자열에 초성, 중성, 종성 추가
                    result := result || chosung[cho + 1] || jungsung[jung + 1] || jongsung[jong + 1];
                ELSE
                    -- 한글이 아닌 경우 그대로 추가
                    result := result || ch;
                END IF;
            END LOOP;
            RETURN result;
        END;
        $$ LANGUAGE plpgsql;
    """)


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
    for idx in range(1, 4):
        await goal_model.TopGoal.create(
            name=f"공부 조지기 {idx}",
            user_id=1,
            show_scope="all",
            tags=["공부", "대학"],
        )
    await goal_model.TopGoal.create(
        name="테스틋-ㅌ셑슽",
        user_id=1,
        show_scope="all",
        tags=["코딩", "공부"],
    )
    await goal_model.TopGoal.create(
        name="헬스조지기",
        user_id=2,
        show_scope="followers",
        tags=["헬스"],
        related_tags=["운동", "건강", "다이어트"],
    )
    await goal_model.TopGoal.create(
        name="게임조지기",
        user_id=3,
        show_scope="followers",
        tags=["게임"],
        related_tags=["컴퓨터", "취미", "여가"],
    )
    await goal_model.TopGoal.create(
        name="코딩조지기",
        user_id=3,
        show_scope="followers",
        tags=["코딩"],
        related_tags=["프로그래밍", "공부", "개발"],
    )
    await goal_model.TopGoal.create(
        name="코딩조지기",
        user_id=4,
        show_scope="followers",
        tags=["코딩"],
        related_tags=["프로그래밍", "공부", "개발"],
    )

    from apps.goal.enum import GoalStatus
    await goal_model.SubGoal.create(
        name="Test subgoal1",
        # plan_datetime=datetime(2024, 12, 30),
        plan_datetime=datetime.now(),
        user_id=2,
        top_goal_id=4,
    )
    await goal_model.SubGoal.create(
        name="Test subgoal2",
        plan_datetime=datetime(2024, 12, 30),
        user_id=3,
        top_goal_id=5,
    )
    await goal_model.SubGoal.create(
        name="하위목표 1",
        plan_datetime=datetime(2024, 12, 30),
        user_id=1,
        top_goal_id=1,
        status=GoalStatus.COMPLETE,
    )
    await goal_model.Reaction.create(
        type=goal_model.ReactionType.EMOTICON,
        content="😔",
        user_id=1,
        sub_goal_id=3,
    )
    await goal_model.Reaction.create(
        type=goal_model.ReactionType.EMOTICON,
        content="😔",
        user_id=1,
        sub_goal_id=3,
    )
    await goal_model.Reaction.create(
        type=goal_model.ReactionType.EMOTICON,
        content="d",
        user_id=1,
        sub_goal_id=3,
    )
    await goal_model.Reaction.create(
        type=goal_model.ReactionType.COMMENT,
        content="지미",
        user_id=1,
        sub_goal_id=3,
    )
    await goal_model.SubGoal.create(
        name="하위목표 2",
        plan_datetime=datetime(2024, 12, 30),
        user_id=1,
        top_goal_id=1,
        status=GoalStatus.COMPLETE,
    )
    await goal_model.SubGoal.create(
        name="하위목표 3",
        plan_datetime=datetime(2024, 12, 30),
        user_id=1,
        top_goal_id=1,
        status=GoalStatus.COMPLETE,
    )
    await goal_model.SubGoal.create(
        name="하위목표 4",
        plan_datetime=datetime(2024, 12, 30),
        user_id=1,
        top_goal_id=1,
        status=GoalStatus.INCOMPLETE,
    )
    await goal_model.SubGoal.create(
        name="하위목표 5",
        plan_datetime=datetime(2024, 12, 30),
        user_id=1,
        top_goal_id=2,
        status=GoalStatus.INCOMPLETE,
    )
    await goal_model.SubGoal.create(
        name="하위목표 6",
        plan_datetime=datetime(2024, 12, 30),
        user_id=1,
        top_goal_id=2,
        status=GoalStatus.INCOMPLETE,
    )

    import apps.calendar.model as calendar_model
    await calendar_model.Calendar.create(name="Test Calendar 1")
    await calendar_model.Calendar.create(name="Test Calendar 2")
    await calendar_model.CalendarUser.bulk_create([
        calendar_model.CalendarUser(user_id=1, calendar_id=1, is_admin=True),
        calendar_model.CalendarUser(user_id=1, calendar_id=2, is_admin=True),
        calendar_model.CalendarUser(user_id=2, calendar_id=1),
        calendar_model.CalendarUser(user_id=3, calendar_id=1),
        calendar_model.CalendarUser(user_id=2, calendar_id=2),
        calendar_model.CalendarUser(user_id=3, calendar_id=2),
    ])
    await goal_model.TopGoal.create(
        name="Test calendar topgoal 1",
        show_scope="group",
        user_id=1,
        calendar_id=1,
    )
    await goal_model.TopGoal.create(
        name="Test calendar topgoal 2",
        user_id=1,
        calendar_id=1,
    )
    await goal_model.SubGoal.create(
        name="그룹모두",
        plan_datetime=datetime(2024, 6, 30),
        user_id=1,
        calendar_id=1,
        top_goal_id=6,
    )
    await goal_model.SubGoal.create(
        name="나만",
        plan_datetime=datetime(2024, 6, 30),
        user_id=1,
        calendar_id=1,
        top_goal_id=7,
    )

    import apps.diary.model as diary_model
    await diary_model.Diary.create(
        title="일기1",
        icon="asd",
        content={},
        show_scope="all",
        user_id=1,
        date="2024-01-01",
    )
    await diary_model.Diary.create(
        title="일기2",
        icon="asd",
        content={},
        show_scope="all",
        user_id=1,
        date="2024-01-01",
    )
    await diary_model.Diary.create(
        title="일기3",
        icon="asd",
        content={},
        show_scope="all",
        user_id=1,
        date="2024-01-01",
    )
