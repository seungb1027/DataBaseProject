from flask import Blueprint, jsonify, render_template, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from config import users_collection

users_bp = Blueprint("users", __name__)

@users_bp.route("/settings", methods=["GET"])
def user_settings_page():
    if "username" not in session:
        return redirect("/")
    return render_template("user_settings.html", username=session["username"])

# 회원가입
@users_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "ID 혹은 비밀번호가 필요합니다."}), 400

    if users_collection.find_one({"username": username}):
        return jsonify({"error": "ID가 이미 존재합니다."}), 400

    hashed_password = generate_password_hash(password)
    users_collection.insert_one({"username": username, "password": hashed_password, "favorites": []})
    return jsonify({"message": "회원가입 성공!"}), 201

# 로그인
@users_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = users_collection.find_one({"username": username})
    if user and check_password_hash(user["password"], password):
        session["username"] = username
        return jsonify({"message": "로그인 성공!"}), 200
    return jsonify({"error": "잘못된 ID 혹은 비밀번호입니다."}), 401

# 회원탈퇴
@users_bp.route("/delete_account", methods=["POST"])
def delete_account():
    """
    회원 탈퇴 처리 라우트
    """
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 403

    try:
        username = session["username"]

        # MongoDB에서 사용자 데이터 삭제
        users_collection.delete_one({"username": username})

        # 세션 초기화
        session.clear()

        return jsonify({"message": "탈퇴 성공."}), 200
    except Exception as e:
        print(f"탈퇴 실패: {e}")
        return jsonify({"error": "탈퇴 실패"}), 500
