import cloudinary.uploader
from fastapi import File


class PetService(object):

    @staticmethod
    def upload_pet_image(pet_id: int, image: File):
        folder = "pet-rescue/" + str(pet_id)
        result = cloudinary.uploader.upload(image, folder=folder)
        return {
            "url": result.get('url')
        }
