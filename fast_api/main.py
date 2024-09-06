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

app = FastAPI()

uri = "mongodb://mongoadmin:mongoadmin@mongo_db:27017/?authMechanism=DEFAULT"
IMAGEDIR = "D:/Project A_Art/fast_api_docker/fast_api/shops"

if not os.path.exists(IMAGEDIR):
    os.makedirs(IMAGEDIR)

app.mount("/images", StaticFiles(directory=IMAGEDIR), name="images")
client = MongoClient(uri, connect=False)
db = client['CoffeeApp']

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
 
class users_record(BaseModel):
    username:str
    password:str
    user_id:str
    email:str
    cof_shop_id:str


# @app.post("/upload-image/")
# async def upload_image(file: UploadFile = UploadFile(...)):
#     contents = await file.read()
#     filepath = os.path.join(IMAGEDIR, file.filename)
#     with open(filepath, "wb") as f:
#         f.write(contents)
#     image_data = {"filename": file.filename, "url": filepath}
#     db.images.insert_one(image_data)
#     return {"filename": file.filename, "url": filepath}

# @app.get("/images/{image_id}")
# async def get_image(image_id: str):
#     image_path = os.path.join(IMAGEDIR, image_id)
#     if not os.path.exists(image_path):
#         raise HTTPException(status_code=404, detail="Image not found")
#     return FileResponse(image_path)

@app.get("/users/")
async def find_user_id():
    users = db.users.find()
    return {"Users": json.loads(json_util.dumps(users))}

@app.get("/username/")
async def find_username(username):
    users = db.users.find_one({'username':username})
    return {"users": json.loads(json_util.dumps(users))}

# @app.get("/test/")
# async def find_coffee_shop():
#     coffee_shops = db.coffee_shops.find()
#     coffee_beans = db.coffee_beans.find()
#     data = coffee_shops+ coffee_beans
#     return {"coffee_shop": json.loads(json_util.dumps(data))}

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



