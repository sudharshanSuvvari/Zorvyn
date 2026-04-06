# app/services/category_service.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ConflictError, ForbiddenOperationError
from app.models.category import Category
from app.repositories.category_repo import CategoryRepository
from app.schemas.category import CategoryCreate

class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CategoryRepository(Category, db)

    async def list_categories(self, type_filter: str | None):
        return await self.repo.list_all(type_filter=type_filter)

    async def create_category(self, payload: CategoryCreate) -> object:
        existing = await self.repo.get_by_name(payload.name)
        if existing:
            raise ConflictError(f"Category '{payload.name}' already exists")

        from app.models.category import Category
        cat = Category(name=payload.name, type=payload.type,
                       color_hex=payload.color_hex, is_system=False)
        created = await self.repo.create(cat)
        await self.db.commit()
        return created

    async def delete_category(self, category_id: int) -> None:
        cat = await self.repo.get_by_id(category_id)
        if not cat:
            raise NotFoundError(f"Category {category_id} not found")
        if cat.is_system:
            raise ForbiddenOperationError("System categories cannot be deleted")

        in_use = await self.repo.is_in_use(category_id)
        if in_use:
            raise ConflictError("Cannot delete a category that is assigned to existing records")

        await self.repo.delete(cat)
        await self.db.commit()