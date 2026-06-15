from typing import Optional, List, Literal

from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator


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
    #author: Author

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
