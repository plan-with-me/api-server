from apps.user import model, enum


async def check_is_following(
    request_user_id: int,
    target_user_id: int,
) -> bool:
    return await model.Follow.filter(
        user_id=request_user_id,
        target_user_id=target_user_id,
    ).exists()
