import logging
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.helpers.login_manager import PermissionRequired
from app.schemas.sche_pet import PetInfoRequest, Urls
from app.services.srv_pet import PetService
from app.services.srv_veterinary_clinic import VeterinaryClinicService

logger = logging.getLogger()
router = APIRouter()


@router.post('', dependencies=[Depends(PermissionRequired('admin', 'volunteer'))])
def create_pet(name: str = Form(...),
               age: str = Form(...),
               gender: str = Form(...),
               color: str = Form(...),
               health_condition: str = Form(...),
               weight: float = Form(...),
               species: str = Form(...),
               description: str = Form(...),
               images: List[UploadFile] = File(...)):

    exist_pet = PetService.is_exist_pet(name=name)
    if exist_pet:
        raise HTTPException(status_code=400, detail='Pet name is already exist')

    if species != 'cat' and species != 'dog':
        raise HTTPException(status_code=400, detail='species chỉ nhận các giá trị cat, dog')
    if age != 'young' and age != 'mature' and age != 'old':
        raise HTTPException(status_code=400, detail='age chỉ nhận các giá trị young, mature, old')
    if gender != 'male' and gender != 'female':
        raise HTTPException(status_code=400, detail='gender chỉ nhận các giá trị male, female')

    pet_info = {
        'name': name,
        'age': age,
        'gender': gender,
        'color': color,
        'health_condition': health_condition,
        'weight': weight,
        'species': species,
        'description': description
    }
    PetService.create_pet(data=pet_info)

    pet_id = PetService.is_exist_pet(name=name)['id']
    for image in images:
        file_name = " ".join(image.filename.strip().split())
        file_ext = file_name.split('.')[-1]
        if file_ext.lower() not in ('jpg', 'png', 'jpeg'):
            raise HTTPException(status_code=400, detail='Can not upload file ' + image.filename)
        PetService.upload_pet_image(pet_id=pet_id, image=image.file)

    return {
        "pet_id": pet_id
    }

@router.get('')
def get_list_pets(species: Optional[str] = None, age: Optional[str] = None, gender: Optional[str] = None):
    pets = PetService.get_list_pets(species=species, age=age, gender=gender)
    for pet in pets:
        images = PetService.get_pet_images(pet_id=pet.get('id'))
        pet['images'] = images
    return {
        'pets': pets
    }

@router.get('/{pet_id}')
def get_pet_by_id(pet_id: int):
    pet = PetService.get_pet_by_id(pet_id=pet_id)
    if pet is None:
        raise HTTPException(status_code=400, detail='Pet not found')
    pet['images'] = PetService.get_pet_images(pet_id=pet_id)
    return pet

@router.put('/{pet_id}', dependencies=[Depends(PermissionRequired('admin', 'volunteer'))])
def update_pet_info(pet_id: int,
                    name: str = Form(None),
                    age: str = Form(None),
                    gender: str = Form(None),
                    color: str = Form(None),
                    health_condition: str = Form(None),
                    weight: float = Form(None),
                    species: str = Form(None),
                    description: str = Form(None),
                    images: List[UploadFile] = File(None)):
    pet = get_pet_by_id(pet_id=pet_id)

    if name is None:
        name = pet.get('name')
    if age is None:
        age = pet.get('age')
    if color is None:
        color = pet.get('color')
    if health_condition is None:
        health_condition = pet.get('health_condition')
    if weight is None:
        weight = pet.get('weight')
    if description is None:
        description = pet.get('description')
    if species is None:
        species = pet.get('species')
    if gender is None:
        gender = pet.get('gender')

    if species != 'dog' and species != 'cat':
        raise HTTPException(status_code=400, detail='species chỉ nhận các giá trị cat, dog')
    if age != 'young' and age != 'mature' and age != 'old':
        raise HTTPException(status_code=400, detail='age chỉ nhận các giá trị young, mature, old')
    if gender != 'male' and gender != 'female':
        raise HTTPException(status_code=400, detail='gender chỉ nhận các giá trị male, female')

    pet_info = {
        'name': name,
        'age': age,
        'gender': gender,
        'color': color,
        'health_condition': health_condition,
        'weight': weight,
        'species': species,
        'description': description
    }
    PetService.update_pet_info(pet_id=pet_id, data=pet_info)

    for image in images:
        file_name = " ".join(image.filename.strip().split())
        file_ext = file_name.split('.')[-1]
        if file_ext.lower() not in ('jpg', 'png', 'jpeg'):
            raise HTTPException(status_code=400, detail='Can not upload file ' + image.filename)
        PetService.upload_pet_image(pet_id=pet_id, image=image.file)

@router.delete('/{pet_id}', dependencies=[Depends(PermissionRequired('admin', 'volunteer'))])
def delete_pet(pet_id: int):
    PetService.delete_pet(pet_id=pet_id)

@router.post('/{pet_id}/images', dependencies=[Depends(PermissionRequired('admin', 'volunteer'))])
def upload_list_pet_images(pet_id: int, images: List[UploadFile] = File(...)):
    pet = PetService.get_pet_by_id(pet_id=pet_id)
    if pet is None:
        raise HTTPException(status_code=400, detail='Pet not found')

    urls = []
    for image in images:
        file_name = " ".join(image.filename.strip().split())
        file_ext = file_name.split('.')[-1]
        if file_ext.lower() not in ('jpg', 'png', 'jpeg'):
            raise HTTPException(status_code=400, detail='Can not upload file ' + image.filename)
        urls.append(PetService.upload_pet_image(pet_id=pet_id, image=image.file))
    return {
        'urls': urls
    }

@router.delete('/{pet_id}/images', dependencies=[Depends(PermissionRequired('admin', 'volunteer'))])
def delete_image(pet_id: int, req: Urls):
    for url in req.urls:
        PetService.delete_image(pet_id=pet_id, url=url)

@router.get('/{pet_id}/health_report', dependencies=[Depends(PermissionRequired('admin', 'volunteer'))])
def get_list_health_report_of_pet(pet_id: int, start_at: Optional[date] = None, end_at: Optional[date] = None):
    pet = PetService.get_pet_by_id(pet_id=pet_id)
    if pet is None:
        raise HTTPException(status_code=400, detail='Pet not found')
    return {
        'health_reports':
            VeterinaryClinicService.get_list_health_reports_by_pet_id_or_veterinary_clinic_id(pet_id=pet_id,
                                                                                              veterinary_clinic_id=None,
                                                                                              start_at=start_at,
                                                                                              end_at=end_at)
    }
