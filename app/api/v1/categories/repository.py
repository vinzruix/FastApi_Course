from typing import Tuple, List, Optional
from unicodedata import category

from sqlalchemy import Sequence, select
from sqlalchemy.orm import Session

from app.api.v1.categories.schemas import CategoryUpdate
from app.models import CategoryORM


class CategoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def list_many(self, *,
                  skip: int = 0,
                  limit: int = 50) -> Sequence[CategoryORM]:  # Asterisco significa no argumentos posiicionales
        # Sequence es una list o una tupla
        query = select(CategoryORM).offset(skip).limit(limit)
        return self.db.execute(query).scalars().all()

    def list_with_total(self, *, page: int = 1, per_page: int = 50) -> Tuple[int, List[CategoryORM]]:
        pass

    def get(self, category_id) -> Optional[CategoryORM]:
        return self.db.get(CategoryORM,category_id)

    def get_by_slug(self,slug : str) -> Optional[CategoryORM]:
        query = select(CategoryORM).where(CategoryORM.slug == slug)
        return self.db.execute(query).scalars().first()

    def create(self, * , name : str, slug : str) -> CategoryORM:
        new_category = CategoryORM(name=name,slug=slug)

        self.db.add(new_category)
        self.db.flush()

        return new_category


    def update(self, category_update : CategoryORM, updates : dict ) -> CategoryORM:

        for key, value in updates.items():
            setattr(category_update,key,value)

        self.db.add(category_update)
        self.db.flush()

        return category_update

    def delete(self, category_to_delete: CategoryORM) -> None:
        self.db.delete(category_to_delete)
