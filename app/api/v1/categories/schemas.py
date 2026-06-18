
from pydantic import BaseModel, Field, ConfigDict


class CategoryBase(BaseModel):
    name : str = Field(min_length=2, max_length=60)
    slug : str = Field(min_length=2,max_length=60)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name : str | None = Field(default=None,min_length=2, max_length=60)
    slug : str | None = Field(default=None,min_length=2,max_length=60)

class CategoryPublic(CategoryUpdate):
    id : int

    model_config = ConfigDict(from_attributes=True)