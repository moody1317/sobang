import client from "./client";

export async function login(firefighterNumber, password, rememberMe = true) {
    const response = await client.post("/auth/login", {
        firefighter_number: firefighterNumber,
        password: password,
    });

    const { access_token, must_change_password } = response.data;
    const storage = rememberMe ? localStorage : sessionStorage;

    localStorage.setItem("access_token", access_token);
    localStorage.setItem("must_change_password", must_change_password);

    return response.data;
}

export async function changePassword(currentPassword, newPassword) {
    const response = await client.post("/auth/change-password", {
        current_password: currentPassword,
        new_password: newPassword,
    });

    localStorage.setItem("must_change_password", "false");

    return response.data;
}

export function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("must_change_password");
}

export function getMustChangePassword() {
    return localStorage.getItem("must_change_password") === "true";
}

export function isLoggedIn() {
    return !!localStorage.getItem("access_token");
}