from flask import Flask, jsonify, redirect, render_template, session
from routes.users import users_bp
from routes.movies import movies_bp
from models import fetch_movies_and_save

app = Flask(__name__)
app.secret_key = "supersecretkey"

check = int;

# 블루프린트 등록
app.register_blueprint(users_bp, url_prefix="/users")
app.register_blueprint(movies_bp, url_prefix="/movies")

def initialize_database():
    """초기화 시 MongoDB에 영화 데이터 저장"""
    print("Initializing database...")
    fetch_movies_and_save(pages=5)  # 약 100개의 영화 저장
    check = 0;
    
@app.route("/")
def home():
    if "username" in session:
        return redirect("/movies")
    return render_template("index.html")

# 로그아웃 라우트
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)  # 세션에서 사용자 정보 제거
    return redirect("/")  # 로그아웃 후 메인 페이지로 리다이렉트

@app.errorhandler(404)
def not_found_error(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # MongoDB 초기화 실행
    if check != 0 :
        initialize_database()
    app.run(debug=True)
