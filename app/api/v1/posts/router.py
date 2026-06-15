import math
from typing import Optional, Literal, List, Union
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from app.core.db import get_db
from .schemas import PostPublic, PaginatedPost, PostCreate, PostUpdate, PostSummary
from .repository import PostRepository
from fastapi import APIRouter, Depends, Path, HTTPException, Query

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=PaginatedPost)
async def list_post(
        query: Optional[str] =
        Query(default=None, description="Text para buscar por titulo", alias="search",
              # alias cambia el nombre en la ruta del param
              min_length=3, max_length=50, pattern=r"[a-zA-Z]+", deprecated=True),
        page: int = Query(default=1, ge=1, description="Pagina a para obtener resultados ( >=1)"),
        per_page: int = Query(default=5, ge=1, le=50, description="Elementos por pagina (>=1  <=50)"),
        order_by: Literal["id", "title"] = Query(default="id", description="Campo por orden"),
        direction: Literal["asc", "desc"] = Query(default="asc", description="Direccion de orden"),
        db: Session = Depends(get_db)):
    repository = PostRepository(db)

    total, items = repository.search(query=query, order_by=order_by, direction=direction, page=page, per_page=per_page)
    total_pages = math.ceil(total / per_page) if total > 0 else 0

    current_page = 1 if total_pages == 0 else min(page, total_pages)

    has_prev = current_page > 1
    has_next = current_page < total_pages if total_pages > 0 else False

    return PaginatedPost(page=page, per_page=per_page, total=total, total_pages=total_pages, has_next=has_next,
                         has_prev=has_prev, order_by=order_by, direction=direction, search=query, items=items)


@router.get("/by-tags", response_model=List[PostPublic])
async def filter_by_tags(
        tags: List[str] = Query(..., min_length=1,
                                description="Busca un post por etiquetas. Ex: ?tags=python&tags=fastapi"),
        db: Session = Depends(get_db)):
    repository = PostRepository(db)

    return repository.by_tags(tags)


@router.get("/{post_id}", response_model=Union[PostPublic, PostSummary])
async def retrieve_post(
        post_id: int = Path(..., ge=1, title="id del post", description="Identificador entero del post, (mayor a 0)",
                            example=1),
        include_content: bool | None = Query(default=True, description="Indica si quiere el contenido del dict o no"),
        db: Session = Depends(get_db)
):
    repository = PostRepository(db)

    post = repository.get(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)

    return PostSummary.model_validate(post, from_attributes=True)


@router.post("", response_model=PostPublic, response_description="Post creado", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    repository = PostRepository(db)

    try:
        post = repository.create_post(title=post.title,
                                      content=post.content,
                                      author=(post.author.model_dump() if post.author else None),
                                      tags=[tag.model_dump() for tag in post.tags])

        db.commit()
        db.refresh(post)
        return post
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El titulo ya existe")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear el post")


@router.put("/{post_id}", response_model=PostPublic, response_description="Post actualizado",
            response_model_exclude_none=True)
async def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db)):
    repository = PostRepository(db)

    post = repository.get(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    try:
        post = repository.update_post(post=post, updates=data.model_dump(exclude_unset=True))
        db.commit()
        db.refresh(post)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="error al actualizar el post")

    return post


@router.delete("{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    repository = PostRepository(db)
    post = repository.get(post_id)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    try:
        repository.delete_post(post)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="error al eliminar")
