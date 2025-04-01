from typing import Optional

from pydantic import BaseModel

from dojocommons.model.app_configuration import AppConfiguration
from dojocommons.model.base_resource import BaseResource
from dojocommons.repository.base_repository import BaseRepository
from dojocommons.service.base_service import BaseService


class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str


class UserResource(BaseResource):
    USERS = "/users"
    USERS_ID = "/users/{id}"


class UserRepository(BaseRepository[User]):
    def __init__(self, cfg: AppConfiguration):
        super().__init__(cfg, User, "users")


class UserService(BaseService[User]):
    def __init__(self, cfg: AppConfiguration):
        super().__init__(cfg, UserRepository)
