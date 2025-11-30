from app.models.roles import RoleModel
from app.repositories.base import BaseRepository
from app.schemes.roles import SRoleGet


class RolesRepository(BaseRepository):
    model = RoleModel
    schema = SRoleGet
