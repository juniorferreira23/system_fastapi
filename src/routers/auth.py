from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models import User
from src.schemas import Token
from src.security import (
    create_access_token,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])

OAuth2FormAnnotated = Annotated[OAuth2PasswordRequestForm, Depends()]
SessionAnnotated = Annotated[AsyncSession, Depends(get_session)]


@router.post('/token', status_code=HTTPStatus.OK, response_model=Token)
async def login_for_acess_token(
    form_data: OAuth2FormAnnotated,
    session: SessionAnnotated,
):
    user = await session.scalar(
        select(User).where(User.username == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='incorrect username or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='incorrect username or password',
        )

    access_token = create_access_token({'sub': user.username})

    return {'access_token': access_token, 'token_type': 'Bearer'}
