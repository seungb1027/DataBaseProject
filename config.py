from pymongo import MongoClient

# MongoDB 설정
def get_db():
    client = MongoClient("") # MongoDB 로컬 주소 작성
    db = client["movie_recommendation"]
    return db

db = get_db()
movies_collection = db["movies"]
users_collection = db["users"]


# TMDb API 설정
API_KEY = ""  # TMDb API 키 입력
BASE_URL = "https://api.themoviedb.org/3"
