import axios from 'axios';

const client = axios.create({
    baseURL: "/api/v1",
    withCredentials: true,
});

// 401 떨어지면 로그인 상태 지우고 로그인 페이지로
client.interceptors.response.use(
    (response) => response,
    (error) => {
        const isLoginRequest = error.config?.url?.includes("/auth/login");

        if (error.response?.status === 401 && !isLoginRequest) {
            localStorage.removeItem("is_logged_in");
            localStorage.removeItem("must_change_password");
            window.location.href = "/";
        }
        return Promise.reject(error);
    }
);

export default client;