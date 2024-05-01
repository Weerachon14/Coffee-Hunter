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
import datetime
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


class review_record(BaseModel):    
    Cof_shop_name:str
    Cof_shop_id:str     
    User_id:str
    rating:str
    rating_id:str
    comment:str
    # last_comment:datetime


@app.post("/reviews/")
async def post_review(review):
    review_dict = review.dict()
    review_dict['date_posted'] = datetime.utcnow()
    db.reviews.insert_one(review_dict)
    return {"message": "Review posted successfully", "review": review_dict}


@app.get("/reviews/{cof_shop_id}")
async def get_reviews(cof_shop_id: str):
    reviews = list(db.reviews.find({"cof_shop_id": cof_shop_id}))
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this coffee shop")

    average_rating = sum(review['rating'] for review in reviews) / len(reviews)
    rating_distribution = {str(star): 0 for star in range(1, 6)}
    for review in reviews:
        star = str(int(round(review['rating'], 0)))
        rating_distribution[star] += 1

    return {
        "average_rating": average_rating,
        "total_reviews": len(reviews),
        "rating_distribution": rating_distribution,
        "reviews": reviews
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



