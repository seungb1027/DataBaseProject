from config import movies_collection, users_collection
from werkzeug.security import generate_password_hash
import requests

BASE_URL = "https://api.themoviedb.org/3"
API_KEY = "393154c2e4ea2fbe26dd7e7aabf21a9b"  # TMDb에서 발급받은 API 키 입력

# 사용자 CRUD
def create_user(data):
    """사용자 생성"""
    username = data["username"]
    password = generate_password_hash(data["password"])
    if users_collection.find_one({"username": username}):
        return None
    users_collection.insert_one({"username": username, "password": password, "favorites": []})
    return username

def get_favorites(username):
    """사용자의 선호 영화 목록 반환"""
    user = users_collection.find_one({"username": username}, {"_id": 0, "favorites": 1})
    return user.get("favorites", []) if user else []

def add_favorite(username, title):
    """사용자의 선호 영화 목록에 영화 추가"""
    users_collection.update_one(
        {"username": username},
        {"$addToSet": {"favorites": title}}
    )

def remove_favorite(username, title):
    """사용자의 선호 영화 목록에서 영화 제거"""
    users_collection.update_one(
        {"username": username},
        {"$pull": {"favorites": title}}
    )

def get_recommended_movies(favorites):
    """사용자의 선호 영화 기반 추천 영화 반환"""
    # 선호 영화의 장르를 기반으로 추천
    favorite_genres = movies_collection.find(
        {"title": {"$in": favorites}}, {"genres": 1, "_id": 0}
    )
    genres = [genre for movie in favorite_genres for genre in movie["genres"]]
    recommendations = movies_collection.find(
        {"genres": {"$in": genres}, "title": {"$nin": favorites}}, {"_id": 0}
    )
    return list(recommendations)

def fetch_genres():
    """TMDb API에서 장르 목록 가져오기"""
    url = f"{BASE_URL}/genre/movie/list?api_key={API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {genre["id"]: genre["name"] for genre in data["genres"]}
    else:
        print(f"Failed to fetch genres: {response.status_code}")
        return {}
    

def fetch_movies_and_save(pages=5):
    """
    TMDb API에서 영화 데이터를 가져와 MongoDB에 저장합니다.
    1 페이지당 약 20개의 영화가 반환되므로, 5페이지를 가져오면 약 100편 저장.
    """
    genres_map = fetch_genres()  # 장르 ID -> 이름 매핑 생성
    total_movies_saved = 0

    for page in range(1, pages + 1):
        url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=en-US&page={page}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            movies = []
            for movie in data["results"]:
                # 장르 ID를 이름으로 변환
                genres = [genres_map.get(genre_id, "Unknown") for genre_id in movie.get("genre_ids", [])]
                movie_data = {
                    "title": movie["title"],
                    "genres": genres,
                    "rating": movie["vote_average"],
                    "release_date": movie.get("release_date", "Unknown"),
                    "poster_url": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None
                }

                # 중복 체크 후 MongoDB에 저장
                if not movies_collection.find_one({"title": movie["title"]}):
                    movies.append(movie_data)

            # MongoDB에 저장
            if movies:
                movies_collection.insert_many(movies)
                total_movies_saved += len(movies)
        else:
            print(f"Failed to fetch movies from page {page}: {response.status_code}")
            break

    print(f"Total movies saved to MongoDB: {total_movies_saved}")
    return total_movies_saved

def get_movies():
    """모든 영화 데이터 반환"""
    return list(movies_collection.find({}, {"_id": 0}))

def get_movie(title):
    """특정 영화 데이터 반환"""
    return movies_collection.find_one({"title": title}, {"_id": 0})

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from config import movies_collection

def calculate_genre_similarity():
    """
    MongoDB의 영화 데이터를 기반으로 장르 유사도를 계산합니다.
    """
    # MongoDB에서 영화 데이터 가져오기
    movies = list(movies_collection.find({}, {"_id": 0, "title": 1, "genres": 1}))

    # 장르 데이터를 문자열로 변환
    movie_df = pd.DataFrame(movies)
    movie_df["genres"] = movie_df["genres"].apply(lambda x: " ".join(x))

    # CountVectorizer로 장르 데이터를 벡터화
    vectorizer = CountVectorizer()
    genre_vectors = vectorizer.fit_transform(movie_df["genres"])

    # 코사인 유사도 계산
    similarity_matrix = cosine_similarity(genre_vectors)

    # 유사도 데이터프레임 생성
    similarity_df = pd.DataFrame(
        similarity_matrix,
        index=movie_df["title"],
        columns=movie_df["title"]
    )
    return similarity_df

def get_recommendations(favorite_movies, similarity_df, top_n=5):
    """
    선호 영화 목록 기반으로 추천 영화 반환.

    파라미터:
        favorite_movies (list): 선호 영화 제목 리스트.
        similarity_df (pd.DataFrame): 영화 간 유사도 데이터프레임.
        top_n (int): 반환할 추천 영화 개수.

    Returns:
        list: 추천 영화 제목 리스트.
    """
    # 모든 선호 영화와 유사한 영화 수집
    all_similar_movies = pd.Series(dtype="float64")
    
    for movie in favorite_movies:
        if movie in similarity_df.index:
            # 각 영화와 유사한 영화를 합산 (중복 허용)
            all_similar_movies = all_similar_movies.add(
                similarity_df[movie], fill_value=0
            )
    
    # 선호 영화 목록 제외
    all_similar_movies = all_similar_movies.drop(index=favorite_movies, errors="ignore")

    # 유사도가 높은 순으로 정렬 후 상위 N개 반환
    recommended_movies = all_similar_movies.sort_values(ascending=False).head(top_n).index.tolist()

    return recommended_movies

