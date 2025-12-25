from app.models.brands import BrandModel
from app.repositories.base import BaseRepository
from app.schemes.brands import BrandGet


class BrandsRepository(BaseRepository):
    model = BrandModel
    schema = BrandGet