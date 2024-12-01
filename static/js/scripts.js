// Navigate to a page
function navigate(url) {
    window.location.href = url;
}

// Logout
async function logout() {
    const response = await fetch("/logout", { method: "POST" });
    if (response.ok) {
        navigate("/");
    }
}
async function deleteAccount() {
    if (confirm("회원 탈퇴를 진행하시겠습니까?")) {
        try {
            const response = await fetch("/users/delete_account", { method: "POST" });

            if (response.ok) {
                const data = await response.json();
                alert(data.message);
                window.location.href = "/"; // 메인 페이지로 리디렉션
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.error}`);
            }
        } catch (error) {
            console.error("회원탈퇴 실패:", error);
            alert("다시 시도해주십시오.");
        }
    }
}


// Add a favorite movie
async function addFavorite(title) {
    await fetch("/movies/add_favorite", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title })
    });
    alert(`${title} 선호 영화에 추가되었습니다!`);
    window.location.reload(); // 페이지 새로고침
}

// Remove a favorite movie
async function removeFavorite(title) {
    await fetch("/movies/remove_favorite", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title })
    });
    alert(`${title} 선호 영화에서 제거되었습니다.`);
    window.location.reload(); // 페이지 새로고침
}

async function updateFavorite(action, title) {
    try {
        const response = await fetch("/movies/favorites", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action, title })
        });        

        if (!response.ok) {
            const errorData = await response.json(); // JSON 에러 읽기
            console.error("Server error:", errorData);
            alert(`Error: ${errorData.error}`);
            return;
        }

        const data = await response.json();
        alert(data.message);

        // 추천 영화 목록 업데이트
        const recommendationsContainer = document.getElementById("recommendations");
        recommendationsContainer.innerHTML = ""; // 기존 추천 목록 삭제

        if (data.recommendations && data.recommendations.length > 0) {
            data.recommendations.forEach((movie) => {
                const movieDiv = document.createElement("div");
                movieDiv.className = "movie";
                movieDiv.innerHTML = `
                    <img src="${movie.poster_url}" alt="${movie.title}">
                    <h3>${movie.title}</h3>
                    <p>Rating: ${movie.rating}</p>
                    <button onclick="updateFavorite('add', '${movie.title}')">Add to Favorites</button>
                `;
                recommendationsContainer.appendChild(movieDiv);
            });
        } else {
            recommendationsContainer.innerHTML = "<p>추천 가능한 영화가 없습니다.</p>";
        }
        window.location.reload(); // 페이지 새로고침
    } catch (error) {
        console.error("업데이트 실패:", error);
        alert("다시 시도해주세요.");
    }
}



// 계정 삭제
async function deleteAccount() {
    const response = await fetch("/users/delete_account", { method: "POST" });
    const data = await response.json();
    alert(data.message || data.error);
    if (response.ok) {
        navigate("/");
    }
}
// API 호출 함수
async function apiCall(endpoint, method = "GET", body = null) {
    const headers = { "Content-Type": "application/json" };
    const options = { method, headers };
    if (body) options.body = JSON.stringify(body);

    const response = await fetch(endpoint, options);
    return response.json();
}

// 회원가입 함수
async function register() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    if (!username || !password) {
        alert("Please fill in both fields.");
        return;
    }

    const response = await apiCall("/users/register", "POST", { username, password });
    alert(response.message || response.error);
}

// 로그인 함수
async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    if (!username || !password) {
        alert("Please fill in both fields.");
        return;
    }

    const response = await apiCall("/users/login", "POST", { username, password });
    if (response.message) {
        alert("로그인 성공!");
        window.location.href = "/movies"; // 영화 목록 페이지로 이동
    } else {
        alert(response.error);
    }
}

