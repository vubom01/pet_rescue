import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.helpers.login_manager import PermissionRequired
from app.schemas.sche_user import UserItemResponse
from app.schemas.sche_work_schedule import WorkSchedule, WorkingDay
from app.services.srv_user import UserService
from app.services.srv_work_schedule import WorkScheduleService

logger = logging.getLogger()
router = APIRouter()

@router.post('', dependencies=[Depends(PermissionRequired('volunteer'))])
def register_work_schedule(request: WorkSchedule,
                           current_user: UserItemResponse = Depends(UserService().get_current_user)):
    res = WorkScheduleService.is_exist_work_schedule(user_id=current_user.get('id'), working_day=request.working_day)
    if res:
        raise HTTPException(status_code=400, detail='You have registered up for the work schedule for this day')
    WorkScheduleService.register_work_schedule(user_id=current_user.get('id'), data=request)

@router.delete('', dependencies=[Depends(PermissionRequired('volunteer'))])
def delete_work_schedule(request: WorkingDay,
                         current_user: UserItemResponse = Depends(UserService().get_current_user)):
    WorkScheduleService.delete_work_schedule(user_id=current_user.get('id'), working_day=request.working_day)

@router.put('', dependencies=[Depends(PermissionRequired('volunteer'))])
def update_work_schedule(request: WorkSchedule,
                         current_user: UserItemResponse = Depends(UserService().get_current_user)):
    res = WorkScheduleService.is_exist_work_schedule(user_id=current_user.get('id'), working_day=request.working_day)
    if res is None:
        raise HTTPException(status_code=400, detail="You don't have registered up for the work schedule for this day")
    WorkScheduleService.update_work_schedule(user_id=current_user.get('id'), data=request)

@router.get('', dependencies=[Depends(PermissionRequired('admin', 'volunteer'))])
def get_list_work_schedule(start_at: Optional[date] = None, end_at: Optional[date] = None):
    list_users = UserService.get_list_volunteers()
    users = []
    for user in list_users:
        work_schedule = WorkScheduleService.get_list_work_schedule_by_user_id(user_id=user.get('id'),
                                                                              start_at=start_at, end_at=end_at)
        users.append({
            'id': user.get('id'),
            'full_name': user.get('first_name') + ' ' + user.get('last_name'),
            'work_schedule': work_schedule
        })
    return {
        'users': users
    }