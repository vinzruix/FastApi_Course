from typing import Optional, List, Literal, Annotated
from fastapi import Form
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator

from app.api.v1.auth.schemas import UserPublic
from app.api.v1.categories.schemas import CategoryPublic


class Tag(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="Nombre de la etiqueta",
    )

    model_config = ConfigDict(from_attributes=True)


# Esto es pydantic
# Se hace varias clases pues pemirte mayor modificacion
class PostBase(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None
    tags: Optional[List[Tag]] = Field(default_factory=list)  # Crea una lista por cada objeto que se cree en el programa
    user: Optional[UserPublic] = None
    category : Optional[CategoryPublic] = None

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
    category_id : Optional[int] = None



    @field_validator("title")
    @classmethod
    def words_not_allowed(cls, value: str) -> str:
        if "puto" in value.lower():
            raise ValueError("El titulo no puede contener la palabra 'puto' ")
        return value

    @classmethod
    def as_form(cls,
                title: Annotated[str, Form(min_length=3)],
                content: Annotated[str, Form(min_length=10)],
                tags : Annotated[Optional[List[str]], Form()] = None,
                category_id : Annotated[int, Form(ge=1)] = None,
                ):

        tag_obj = [Tag(name=tag) for tag in (tags or [])]
        return cls(title=title,tags=tag_obj,content=content, category_id=category_id)


class PostPublic(PostBase):
    id: int
    slug : str

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
