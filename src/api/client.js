import axios from 'axios';

const client = axios.create({
    baseURL: "http://127.0.0.1:8000/api/v1",
});

// 요청마다 토큰 자동으로 헤더에 붙여줌
client.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// 401 떨어지면 토큰 지우고 로그인 페이지로
client.interceptors.response.use(
    (response) => response,
    (error) => {
        const isLoginRequest = error.config?.url?.includes("/auth/login");

        if (error.response?.status === 401 && !isLoginRequest) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("must_change_password");
            window.location.href = "/";
        }
        return Promise.reject(error);
    }
);

export default client;