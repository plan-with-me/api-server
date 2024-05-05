from fastapi import APIRouter, Request, Depends, status, HTTPException

from tortoise.transactions import atomic

from core.dependency import Auth
from apps.todo import model, dto


router = APIRouter(
    prefix="/todo-groups",
    tags=["Todo"],
)


@router.post(
    path="",
    dependencies=[Depends(Auth())],
    response_model=dto.TodoGroupResponse,
)
@atomic()
async def create_todo_group(
    request: Request,
    form: dto.TodoGroupForm,
):
    todo_group = await model.TodoGroup.create(
        **form.__dict__,
        user_id=request.state.token_payload["id"],
    )
    return dto.TodoGroupResponse(**todo_group.__dict__)


@router.get(
    path="",
    dependencies=[Depends(Auth())],
    response_model=list[dto.TodoGroupResponse],
)
async def get_my_todo_groups(request: Request):
    request_user_id = request.state.token_payload["id"]
    todo_groups = await model.TodoGroup.filter(user_id=request_user_id).all()
    return [ 
        dto.TodoGroupResponse(**todo_group.__dict__) 
        for todo_group in todo_groups
    ]


@router.post(
    path="/{todo_group_id}",
    dependencies=[Depends(Auth())],
    response_model=dto.TodoRepsonse,
)
@atomic()
async def create_todo(
    request: Request,
    todo_group_id: int,
    form: dto.TodoForm,
):
    request_user_id = request.state.token_payload["id"]
    todo_group = await model.TodoGroup.get(id=todo_group_id)
    if todo_group.user_id != request_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    todo = await model.Todo.create(
        **form.__dict__,
        user_id=request_user_id,
        todo_group_id=todo_group_id,
    )
    return dto.TodoRepsonse(**todo.__dict__)


@router.get(
    path="/{todo_group_id}/todos",
    dependencies=[Depends(Auth())],
    response_model=list[dto.TodoRepsonse],
)
async def get_my_todos(request: Request):
    request_user_id = request.state.token_payload["id"]
    todos = await model.Todo.filter(
        user_id=request_user_id,
    ).all()
    return [
        dto.TodoRepsonse(**todo.__dict__)
        for todo in todos
    ]
