from fastapi import APIRouter,HTTPException,requests,Depends
from sqlalchemy.orm import Session
from api.auth import Auth
from db.models import User
from db.database import get_db
from db.schemas import PermissionCheckRequest,PermissionResult
router=APIRouter()


def check_permission(user: User, permission: str) -> PermissionResult:
    # Định nghĩa quyền theo role
    permission_rules = {
        "enhance_image": ["plus", "pro", "admin"],
        "premium_feature": ["pro", "admin"],
        # Thêm các quyền/tính năng khác ở đây
        "speech_to_text": ["plus","pro", "admin"],
        "text_to_video": ["plus","pro", "admin"]
    }
    
    allowed_roles = permission_rules.get(permission, [])
    if user.role in allowed_roles:
        return PermissionResult(allowed=True)
    else:
        return PermissionResult(
            allowed=False,
            reason=f"Yêu cầu role {', '.join(allowed_roles)} để truy cập {permission}"
        )
    
@router.post("/check-permissions")
async def check_permissions(
    request: PermissionCheckRequest,
    current_user: User=Depends(Auth.get_current_user),
    db: Session= Depends(get_db)
):
    result=[]
    for permission in request.permissions:
        result[permission]=check_permission(current_user,permission)
    return result

    
