from pymongo import MongoClient

# MongoDB 설정
def get_db():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["movie_recommendation"]
    return db

db = get_db()
movies_collection = db["movies"]
users_collection = db["users"]


# TMDb API 설정
API_KEY = "393154c2e4ea2fbe26dd7e7aabf21a9b"  # TMDb API 키 입력
BASE_URL = "https://api.themoviedb.org/3"
