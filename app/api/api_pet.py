from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
import logging
from pydantic import BaseModel

from app.core.security import create_access_token
from app.helpers.login_manager import login_required, PermissionRequired
from app.schemas.sche_token import Token
from app.schemas.sche_user import UserItemResponse
from app.services.srv_pet import PetService
from app.services.srv_user import UserService

logger = logging.getLogger()
router = APIRouter()


@router.put('/images', dependencies=[Depends(PermissionRequired('admin'))])
def upload_pet_image(pet_id: int, file: UploadFile = File(...)):
    return PetService.upload_pet_image(pet_id=pet_id, image=file.file)


@router.get('', dependencies=[Depends(login_required)], response_model=ListUsers)
def get_list_users():
    users = UserService.get_list_users()
    return {
        'users': users
    }

@router.get('', dependencies=[Depends(login_required)], response_model=PetItemResponse)
@router.get('/me', dependencies=[Depends(login_required)], response_model=UserItemResponse)
def detail_me(current_user: UserItemResponse = Depends(UserService().get_current_user)):
    return current_user