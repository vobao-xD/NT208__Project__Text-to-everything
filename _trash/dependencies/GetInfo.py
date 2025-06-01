from fastapi import Depends, HTTPException, Header, status
from typing import Optional

async def get_current_user(
        x_user_email:Optional[str]=Header(None),
        x_user_role:Optional[str]=Header(None)
):
    if not x_user_email or not x_user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return {"email": x_user_email, "role": x_user_role}
async def get_current_user_email(
    x_user_email:Optional[str]=Header(None)
):
    if not x_user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return x_user_email
async def get_current_user_role(
    x_user_role:Optional[str]=Header(None)
):
    if not x_user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return x_user_role