from fastapi import FastAPI, HTTPException, File , UploadFile
from bson import ObjectId, json_util
import json
from pydantic import BaseModel
from pymongo.mongo_client import MongoClient
from typing import List
import uuid
from fastapi.responses import FileResponse
import os
import shutil
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from model.user import *

import secrets
app = FastAPI()

uri = "mongodb://mongoadmin:mongoadmin@mongo_db:27017/?authMechanism=DEFAULT"
IMAGEDIR = "D:/Project A_Art/fast_api_docker/fast_api/shops"

if not os.path.exists(IMAGEDIR):
    os.makedirs(IMAGEDIR)

app.mount("/images", StaticFiles(directory=IMAGEDIR), name="images")
client = MongoClient(uri, connect=False)
db = client['CoffeeApp']


SECRET_KEY = secrets.token_hex(32)


class Images(BaseModel):
    filename: str
    url: str 

class coffee_bean_record(BaseModel):
    Cof_shop_id:str
    bean_name:str
    price:str
    weigth:str
    origin:str
    Varieties:str
    Altitude:str
    Process:str
    Tasting_Notes:str
    Recommend:str
    Images_url: str

class coffee_shop_record(BaseModel):
    Cof_shop_name:str
    Cof_shop_id:str     
    Opening:str
    Location:str
    rating_total:str
    Images_url: str

class menu_record(BaseModel):
    Cof_shop_id:str
    Menu_name:str
    Description:str
    Coffee_price:str
    Images_url: str
    
class popular_coffee_shop_record(BaseModel):
    Cof_shop_id:str
    Cof_shop_name:str
    rating_id:str
    Images_url:str
      
class review_record(BaseModel):    
    Cof_shop_name:str
    Cof_shop_id:str     
    User_id:str
    rating:str
    rating_id:str
    comment:str
    # last_comment:datetime
 
# class users_record(BaseModel):
#     username:str
#     password:str
#     user_id:str
#     email:str
#     cof_shop_id:str

@app.get("/users/")
async def find_user_id():
    users = db.users.find()
    return {"Users": json.loads(json_util.dumps(users))}

@app.get("/username/")
async def find_username(username):
    users = db.users.find_one({'username':username})
    return {"users": json.loads(json_util.dumps(users))}


@app.get("/coffee_shop/")
async def find_coffee_shop():
    coffee_shops = db.coffee_shops.find()
    return {"coffee_shop": json.loads(json_util.dumps(coffee_shops))}

@app.get("/Pop_shop/")
async def find_pop_coffee_shop():
    pop_shops = db.popular_coffee_shops.find()
    return {"Pop_shop": json.loads(json_util.dumps(pop_shops))}

@app.get("/coffee_bean/")
async def find_coffee_bean():
    coffee_beans = db.coffee_beans.find()
    return {"coffee_bean": json.loads(json_util.dumps(coffee_beans))}

@app.get("/review/")
async def find_review():
    reviews = db.reviews.find()
    return {"review": json.loads(json_util.dumps(reviews))}

@app.get("/Homepage/")
async def find_coffee_shop():
    coffee_shops = list(db.coffee_shops.find())
    popular = list(db.popular_coffee_shops.find())
    menu = list(db.menus.find())
    
    return {
        "coffee_shop": json.loads(json_util.dumps(coffee_shops)),
        "coffee_beans": json.loads(json_util.dumps(popular)),
        "menu": json.loads(json_util.dumps(menu))
    }



@app.get("/Coffee_shop_page/")
async def find_coffee_shop():
    coffee_shops = list(db.coffee_shops.find())
    coffee_beans = list(db.coffee_beans.find())
    menu = list(db.menus.find())
    review = list(db.review.find())
    user = list(db.users.find())
    
    return {
        "coffee_shop": json.loads(json_util.dumps(coffee_shops)),
        "coffee_beans": json.loads(json_util.dumps(coffee_beans)),
        "menu": json.loads(json_util.dumps(menu)),
        "review": json.loads(json_util.dumps(review)),
        "user": json.loads(json_util.dumps(user))
    }


@app.post("/upload_image/")
async def upload_image(file: UploadFile = File(...)):
    # Generate a unique filename to avoid conflicts
    file_extension = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(IMAGEDIR, unique_filename)

    # Save the file to the specified directory
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Store image data in MongoDB (assuming db setup is already done)
    image_data = {
        "filename": unique_filename,
        "url": f"/images/{unique_filename}"
    }
    db.Images.insert_one(image_data)

    # Return the filename and URL where the image can be accessed
    return {"filename": unique_filename, "url": f"/images/{unique_filename}"}


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


#create JWT token
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt



@app.post("/register/")
def register_user(register_request: RegisterRequest):
    hashed_password = pwd_context.hash(register_request.password)
    new_user = users_record(username=register_request.username, email=register_request.email, hashed_password=hashed_password)
    db.user.insert_one(new_user.dict()).__inserted_id
    return {"message": "User registered successfully"}

@app.post("/login/")
def login_user(login_request: LoginRequest):

    user = db.user.find_one({
    "$or": [
        {"username": login_request.username},
        {"email": login_request.username}
    ]
})
    if user and pwd_context.verify(login_request.password, user["hashed_password"]):
        # Create JWT token with user's username and expiration time
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer","username":user["username"]}
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

#users ทั้งหมด
@app.get("/all/")
def get_all_users():
    users = db.user.find()
    #print(product,type(product))
    return {"users": json.loads(json_util.dumps(users))}
#สร้าง user
@app.post("/users/")
def create_user(user_data: users_record):
    user_id = db.user.insert_one(user_data.dict()).inserted_id
    return {"users": "User created successfully", "user_id": str(user_id)}
#เรียก user
@app.get("/users/{users_id}")
def get_user(users_id: str):
    user = db.user.find_one({"_id": ObjectId(users_id)})
    if user:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")
#edit user
@app.put("/users/{users_id}")
def update_user(users_id: str, users_data: dict):
    result = db.user.update_one({"_id": ObjectId(users_id)}, {"$set": users_data})
    if result.modified_count == 1:
        return {"message": "User updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")
#delete user
@app.delete("/users/{users_id}")
def delete_user(users_id: str):
    result = db.user.delete_one({"_id": ObjectId(users_id)})
    if result.deleted_count == 1:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")