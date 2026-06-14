import math
from datetime import datetime
from enum import nonmember
from typing import Optional, List, Union, Literal
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.params import Query, Body, Path
from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from sqlalchemy import create_engine, Integer, String, Text, DateTime, select, func, delete, UniqueConstraint, \
    ForeignKey, Table, Column
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, Mapped, mapped_column, relationship, selectinload, \
    joinedload

load_dotenv()



post_tags = Table("post_tags", Base.metadata,
                  Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
                  Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True))


class AuthorORM(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    posts: Mapped[List["PostORM"]] = relationship(back_populates="author")


class TagORM(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    posts: Mapped[List["PostORM"]] = relationship(secondary=post_tags, back_populates="tags", lazy="selectin")


class PostORM(Base):
    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("title", name="unique_post_title"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("authors.id"))
    author: Mapped[Optional["AuthorORM"]] = relationship(back_populates="posts")
    tags: Mapped[List["TagORM"]] = relationship(secondary=post_tags, back_populates="posts", lazy="selectin",
                                                passive_deletes=True)


Base.metadata.create_all(bind=engine)  # Esto es por ahora, para lo real se usan migraciones

app = FastAPI(
    title="Mini Blog"
)


class Tag(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="Nombre de la etiqueta",
    )

    model_config = ConfigDict(from_attributes=True)


class Author(BaseModel):
    name: str = Field(..., min_length=3, max_length=30, description="Nombre del autor")
    email: EmailStr = Field(..., description="Email del autor")

    model_config = ConfigDict(from_attributes=True)


# Esto es pydantic
# Se hace varias clases pues pemirte mayor modificacion
class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = Field(default_factory=list)  # Crea una lista por cada objeto que se cree en el programa
    author: Optional[Author] = None

    model_config = ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    title: str = Field(
        ...,  # Estas elipsis indican que es obligatorio
        min_length=3,
        max_length=100,
        description="Titulo del post (min 3 ch, max 100 ch)",
        examples=["Django", "FastApi"]
    )
    content: Optional[str] = Field(
        default="Contenido pendiente",
        min_length=10,
        description="Contenido del post (min 10 ch)",
        examples=["Contenido por largo valido =D"]
    )

    tags: Optional[List[Tag]] = Field(default_factory=list)
    author: Author

    @field_validator("title")
    @classmethod
    def words_not_allowed(cls, value: str) -> str:
        if "puto" in value.lower():
            raise ValueError("El titulo no puede contener la palabra 'puto' ")
        return value


class PostPublic(PostBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PostSummary(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = "Default value"


class PaginatedPost(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["title", "id"]
    direction: Literal["asc", "desc"]
    search: Optional[str] = None
    items: List[PostPublic]


@app.get("/")
async def root():
    return {"message": "Bievenidos a mini Blog"}


# QUERY PARAMS
@app.get("/posts", response_model=PaginatedPost)
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
    results = select(PostORM)

    if query:
        results = results.where(PostORM.title.ilike(f"%{query}%"))

        # results = [post for post in BLOG_POST if
        #          query.lower() in post["title"].lower()]  # list compression. Misma logica que las 3 lineas de abajo
        # for post in BLOG_POST:
        #    if query.lower() in post["title"].lower():
        #        results.append(post)

    total = db.scalar(select(func.count()).select_from(results.subquery())) or 0
    total_pages = math.ceil(total / per_page) if total > 0 else 0

    current_page = 1 if total_pages == 0 else min(page, total_pages)

    if order_by == "id":
        order_col = PostORM.id
    else:
        order_col = func.lower(PostORM.title)

    results = results.order_by(order_col.asc() if direction == "asc" else order_col.desc())

    if total_pages == 0:
        items: List[PostORM] = []
    else:
        start = (current_page - 1) * per_page
        # items = results[start: start + per_page]  # [10:20]
        items = db.execute(results.limit(per_page).offset(start)).scalars().all()

    has_prev = current_page > 1
    has_next = current_page < total_pages if total_pages > 0 else False

    return PaginatedPost(page=page, per_page=per_page, total=total, total_pages=total_pages, has_next=has_next,
                         has_prev=has_prev, order_by=order_by, direction=direction, search=query, items=items)


@app.get("/posts/by-tags", response_model=List[PostPublic])
async def filter_by_tags(
        tags: List[str] = Query(..., min_length=1,
                                description="Busca un post por etiquetas. Ex: ?tags=python&tags=fastapi"),
        db: Session = Depends(get_db)):
    normalize_tag_names = [tag.strip().lower() for tag in tags if tag.strip()]

    if not normalize_tag_names:
        return []

    post_list = (select(PostORM).options(selectinload(PostORM.tags), joinedload(PostORM.author)).where(
        PostORM.tags.any(func.lower(TagORM.name).in_(normalize_tag_names))).order_by(PostORM.id.asc()))

    posts = db.execute(post_list).scalars().all()

    return posts


# Path parameter


@app.get("/posts/{post_id}", response_model=Union[
    PostPublic, PostSummary])  # Esto lo que hace es mostrar la response en base a la respuesta que se adapte, para no soltar erorr si no hay content
async def retrieve_post(
        post_id: int = Path(..., ge=1, title="id del post", description="Identificador entero del post, (mayor a 0)",
                            example=1),
        include_content: bool | None = Query(default=True,
                                             description="Indica si quiere el contenido del dict o no"),
        db: Session = Depends(get_db)
):
    find_post = select(PostORM).where(PostORM.id == post_id)
    post = db.execute(find_post).scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)

    return PostSummary.model_validate(post, from_attributes=True)


# ...   esos tres puntos se llaman elipsis
@app.post("/posts", response_model=PostPublic, response_description="Post creado", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    author_obj = None

    if post.author:
        db.execute(select(AuthorORM).where(AuthorORM.email == post.author.email)).scalar_one_or_none()

        if not author_obj:
            author_obj = AuthorORM(name=post.author.name, email=post.author.email)
            db.add(author_obj)
            db.flush()

    new_post = PostORM(title=post.title, content=post.content, author=author_obj)

    for tag in post.tags:
        tag_obj = db.execute(select(TagORM).where(TagORM.name.ilike(f"%{tag.name}%"))).scalar_one_or_none()

        if not tag_obj:
            tag_obj = TagORM(name=tag.name)

            db.add(tag_obj)
            db.flush()

        new_post.tags.append(tag_obj)

    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El titulo ya existe")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear el post")

    # new_id = (BLOG_POST[-1]["id"] + 1) if BLOG_POST else -1
    #
    # new_post = {"id": new_id, "title": post.title, "content": post.content,
    #            "tags": [tag.model_dump() for tag in post.tags], "author": post.author.model_dump()}
    # BLOG_POST.append(new_post)

    # return new_post


@app.put("/posts/{post_id}", response_model=PostPublic, response_description="Post actualizado",
         response_model_exclude_none=True)
async def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db)):
    post = db.get(PostORM, post_id)  # Obtiene un objeto de una tabla por su id

    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    updates = data.model_dump(exclude_unset=True)  # pasa de objeto a dict

    for key, value in updates.items():
        setattr(post, key, value)  # de un objeto busca un llave y le aplica un valor

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(PostORM, post_id)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db.delete(post)
    db.commit()

    return
