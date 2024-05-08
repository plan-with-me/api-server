from apps.calendar import model
from apps.user import model as user_model


async def add_users_on_calendar(
    calendar_id: int, 
    user_ids: list[int],
    validate_strictly: bool = True,
) -> None:
    user_ids = list(set(user_ids))
    if validate_strictly:
        calendar_users = await model.CalendarUser.filter(id=calendar_id).all()
        exist_member_ids = [calendar_user.user_id for calendar_user in calendar_users]
        user_ids = [user_id for user_id in user_ids if user_id not in exist_member_ids]
    
    await model.CalendarUser.bulk_create([
        model.CalendarUser(
            user_id=user_id,
            calendar_id=calendar_id,
        )
        for user_id in user_ids
    ])


async def get_calendar_members(calendar_id: int) -> list[user_model.User]:
    calendar_users = await (model.CalendarUser
                   .filter(calendar_id=calendar_id)
                   .select_related("user")
                   .all())
    users = [calendar_user.user for calendar_user in calendar_users]
    return users
