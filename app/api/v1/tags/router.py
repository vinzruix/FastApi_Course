from unicodedata import name

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.params import Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.tags.repository import TagRepository
from app.api.v1.tags.schemas import TagPublic, TagCreate, TagUpdate
from app.core.db import get_db
from app.core.security import get_current_user, require_editor
from app.models import UserORM

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=dict)
async def list_tags(page: int = Query(1, ge=1),
                    per_page: int = Query(10, ge=1, le=100),
                    order_by: str = Query("id", pattern="^(id|name)"),
                    direction: str = Query("asc", pattern="^(asc|desc)"),
                    search: str | None = Query(None),
                    db: Session = Depends(get_db),
                    ):
    repository = TagRepository(db=db)

    return await repository.list_tags(search=search, page=page, per_page=per_page, order_by=order_by,
                                      direction=direction)


@router.get("/popular/top")
async def get_most_popular_tag(db: Session = Depends(get_db)):
    repository = TagRepository(db=db)

    row = await repository.most_popular()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No hay tags")

    return row

@router.post("", response_model=TagPublic, response_description="Tag creado (OK)", status_code=status.HTTP_201_CREATED)
async def create_tags(tag: TagCreate, db: Session = Depends(get_db), _editor : UserORM = Depends(require_editor)):
    repository = TagRepository(db=db)

    try:
        tag_created = repository.create_tag(tag.name)
        db.commit()
        db.refresh(tag_created)
        return tag_created

    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el tag")


@router.put("/{tag_id}", response_model=TagPublic)
async def update_tag(tag_id: int,
                     payload: TagUpdate,
                     db: Session = Depends(get_db),
                     user=Depends(get_current_user)):
    repo = TagRepository(db)

    try:
        tag_updated = await repo.update(tag_id=tag_id, name=payload.name)

        if not tag_updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag no encontrado")

        db.commit()
        db.refresh(tag_updated)
        return TagPublic.model_validate(tag_updated)

    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear")


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int,
                     db: Session = Depends(get_db),
                     user=Depends(get_current_user)):
    repo = TagRepository(db)

    try:
        tag_deleted_status = await repo.delete(tag_id=tag_id)

        if not tag_deleted_status:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag no encontrado")
        db.commit()

        return

    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al borrar")
