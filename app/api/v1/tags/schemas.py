from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TagPublic(BaseModel):
    id: int
    name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="Nombre de la etiqueta",
    )

    model_config = ConfigDict(from_attributes=True)


class TagCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="Nombre de la etiqueta",
    )


class TagUpdate(BaseModel):
    name: Optional[str] = Field(
        ...,
        min_length=2,
        max_length=30,
        description="Nombre de la etiqueta",
    )

class TagWithCount(TagPublic):
    uses : int
