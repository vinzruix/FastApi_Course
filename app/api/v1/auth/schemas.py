from typing import Optional, Literal
from pydantic import ConfigDict, BaseModel, Field, EmailStr

Role = Literal["user","editor","admin"]

class UserBase(BaseModel):
    email : str
    full_name : Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email : EmailStr
    password : str = Field(max_length=72,min_length=6)
    full_name : Optional[str] = None

class UserLogin(BaseModel):
    email : EmailStr
    password : str

class UserPublic(UserBase):
    id : int
    role : Role
    is_active : bool

class TokenResponse(BaseModel):
    access_token : str
    token_type : str = "bearer"
    user : UserPublic


class RoleUpdate(BaseModel):
    role : Role

class TokenData(BaseModel):
    sub : str
    username : str


