from flask import Blueprint, jsonify, render_template, request, session, redirect
from models import get_movies, get_movie, get_favorites, add_favorite, get_recommendations, remove_favorite, calculate_genre_similarity

movies_bp = Blueprint("movies", __name__)

@movies_bp.route("/", methods=["GET"])
def movies_page():
    if "username" not in session:
        return redirect("/")
    movies = get_movies()
    return render_template("movies.html", movies=movies, username=session["username"])

@movies_bp.route("/<title>", methods=["GET"])
def movie_info(title):
    if "username" not in session:
        return redirect("/")
    movie = get_movie(title)
    return render_template("movie_info.html", movie=movie, username=session["username"])

# @movies_bp.route("/favorites", methods=["GET"])
# def favorites_page():
#     if "username" not in session:
#         return redirect("/")
#     favorites = get_favorites(session["username"])  # 선호 영화 목록
#     movies = [get_movie(title) for title in favorites]  # 선호 영화 데이터
#     recommendations = get_recommended_movies(favorites)  # 추천 영화 (최대 5개는 템플릿에서 처리)
#     return render_template("favorites.html", favorites=movies, recommendations=recommendations, username=session["username"])

# @movies_bp.route("/favorites", methods=["GET", "POST"])
# def favorites_page():
#     if "username" not in session:
#         return redirect("/")

#     # POST 요청 처리 (선호 영화 추가/삭제)
#     if request.method == "POST":
#         data = request.json
#         action = data.get("action")
#         movie_title = data.get("title")

#         if not action or not movie_title:
#             return jsonify({"error": "Invalid request"}), 400

#         # 선호 영화 추가/삭제
#         if action == "add":
#             add_favorite(session["username"], movie_title)
#         elif action == "remove":
#             remove_favorite(session["username"], movie_title)
#         else:
#             return jsonify({"error": "Invalid action"}), 400

#         # 추천 영화 목록 업데이트
#         favorites = get_favorites(session["username"])
#         if favorites:
#             similarity_df = calculate_genre_similarity()
#             recommended_movies = []
#             for favorite in favorites:
#                 recommended_movies += get_similar_movies(favorite, similarity_df)
#             recommended_movies = list({movie: None for movie in recommended_movies}.keys())[:5]
#             recommendations_data = [get_movie(title) for title in recommended_movies]
#         else:
#             recommendations_data = []

#         return jsonify({"message": "Favorites updated", "recommendations": recommendations_data}), 200

#     # GET 요청 처리 (Favorites 페이지 렌더링)
#     favorites = get_favorites(session["username"])
#     movies = [get_movie(title) for title in favorites]

#     if favorites:
#         similarity_df = calculate_genre_similarity()
#         recommended_movies = []
#         for favorite in favorites:
#             recommended_movies += get_similar_movies(favorite, similarity_df)
#         recommended_movies = list({movie: None for movie in recommended_movies}.keys())[:5]
#         recommendations_data = [get_movie(title) for title in recommended_movies]
#     else:
#         recommendations_data = []

#     return render_template(
#         "favorites.html",
#         favorites=movies,
#         recommendations=recommendations_data,
#         username=session["username"]
#     )

@movies_bp.route("/favorites", methods=["GET", "POST"])
def favorites_page():
    if "username" not in session:
        return redirect("/")

    # POST 요청 처리 (선호 영화 추가/삭제)
    if request.method == "POST":
        data = request.json
        action = data.get("action")
        movie_title = data.get("title")

        if not action or not movie_title:
            return jsonify({"error": "Invalid request"}), 400

        # 선호 영화 추가/삭제
        if action == "add":
            add_favorite(session["username"], movie_title)
        elif action == "remove":
            remove_favorite(session["username"], movie_title)
        else:
            return jsonify({"error": "Invalid action"}), 400

        # 추천 영화 목록 업데이트
        favorites = get_favorites(session["username"])
        if favorites:
            similarity_df = calculate_genre_similarity()

            # 선호 영화 목록 기반 추천 영화 생성
            recommended_movies = get_recommendations(favorites, similarity_df, top_n=5)

            # 추천 영화 데이터를 MongoDB에서 가져오기
            recommendations_data = [get_movie(title) for title in recommended_movies]
        else:
            recommendations_data = []

        return jsonify({"message": "Favorites updated", "recommendations": recommendations_data}), 200

    # GET 요청 처리 (Favorites 페이지 렌더링)
    favorites = get_favorites(session["username"])
    movies = [get_movie(title) for title in favorites]

    if favorites:
        similarity_df = calculate_genre_similarity()

        # 선호 영화 목록 기반 추천 영화 생성
        recommended_movies = get_recommendations(favorites, similarity_df, top_n=5)

        # 추천 영화 데이터를 MongoDB에서 가져오기
        recommendations_data = [get_movie(title) for title in recommended_movies]
    else:
        recommendations_data = []

    return render_template(
        "favorites.html",
        favorites=movies,
        recommendations=recommendations_data,
        username=session["username"]
    )

@movies_bp.route("/add_favorite", methods=["POST"])
def add_favorite_movie():
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 403
    data = request.json
    add_favorite(session["username"], data["title"])
    return jsonify({"message": "Movie added to favorites"})

@movies_bp.route("/remove_favorite", methods=["POST"])
def remove_favorite_movie():
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 403
    data = request.json
    remove_favorite(session["username"], data["title"])
    return jsonify({"message": "Movie removed from favorites"})
