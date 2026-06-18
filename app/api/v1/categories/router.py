from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status
from app.api.v1.categories.repository import CategoryRepository
from app.api.v1.categories.schemas import CategoryPublic, CategoryCreate, CategoryUpdate
from app.core.db import get_db

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[CategoryPublic])
def list_categories(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    repository = CategoryRepository(db=db)
    return repository.list_many(skip=skip, limit=limit)  ## El OBLOGA A USAR KEYBOARD ARGUMENTS


@router.post("", response_model=CategoryPublic)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    repository = CategoryRepository(db=db)
    exist = repository.get_by_slug(data.slug)

    if exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug en uso")

    category = repository.create(name=data.name, slug=data.slug)

    db.commit()
    db.refresh(category)

    return category


@router.get("/{category_id}", response_model=CategoryPublic)
def get_category_by_id(category_id: int, db: Session = Depends(get_db)):
    repository = CategoryRepository(db=db)
    category = repository.get(category_id)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria no encotrada")

    return category


@router.put("/{category_id}", response_model=CategoryPublic)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    repository = CategoryRepository(db=db)
    category = repository.get(category_id)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria no encotrada")

    category = repository.update(category_update=category, updates=data.model_dump(exclude_unset=True))

    db.commit()
    db.refresh(category)

    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_category(category_id: int, db: Session = Depends(get_db)):
    repository = CategoryRepository(db=db)
    category = repository.get(category_id)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria no encotrada")

    repository.delete(category_to_delete=category)

    db.commit()

    return None
