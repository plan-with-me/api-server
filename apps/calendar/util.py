from apps.calendar import model
from apps.user import model as user_model


async def set_users_on_calendar(
    calendar_id: int, 
    new_user_ids: list[int],
    validate_strictly: bool = True,
) -> None:
    new_user_ids = list(set(new_user_ids))
    if validate_strictly:
        calendar_users = await model.CalendarUser.filter(id=calendar_id).all()
        exist_user_ids = [calendar_user.user_id for calendar_user in calendar_users]
        new_user_ids = [user_id for user_id in new_user_ids if user_id not in exist_user_ids]
        delete_user_ids = [user_id for user_id in exist_user_ids if user_id not in new_user_ids]
        await model.CalendarUser.filter(user_id__in=delete_user_ids).delete()
    
    await model.CalendarUser.bulk_create([
        model.CalendarUser(
            user_id=user_id,
            calendar_id=calendar_id,
        )
        for user_id in new_user_ids
    ])


async def get_calendar_members(calendar_id: int) -> list[user_model.User]:
    calendar_users = await (model.CalendarUser
                   .filter(calendar_id=calendar_id)
                   .select_related("user")
                   .all())
    users = [calendar_user.user for calendar_user in calendar_users]
    return users
