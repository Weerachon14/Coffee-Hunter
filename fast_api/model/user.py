from pydantic import BaseModel,validator
from typing import Optional

class users_record(BaseModel):
    username:str
    user_id:Optional [str]
    email:str
    cof_shop_id: Optional [str]
    hashed_password:str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str