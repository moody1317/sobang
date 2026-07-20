import client from "./client";

export async function login(firefighterNumber, password) {
    const response = await client.post("/auth/login", {
        firefighter_number: firefighterNumber,
        password: password,
    });

    const { must_change_password } = response.data;

    localStorage.setItem("is_logged_in", "true");
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
    client.post("/auth/logout").catch(() => {});
    localStorage.removeItem("is_logged_in");
    localStorage.removeItem("must_change_password");
}

export function getMustChangePassword() {
    return localStorage.getItem("must_change_password") === "true";
}

export function isLoggedIn() {
    return localStorage.getItem("is_logged_in") === "true";
}

export async function getMe() {
    const response = await client.get("/auth/me");
    return response.data;
}

export async function verifyPassword(password) {
    const response = await client.post("/auth/verify-password", { password });
    return response.data;
}

export async function updateProfile(data) {
    const response = await client.patch("/auth/me", data);
    return response.data;
}

export async function getStationUsers() {
    const response = await client.get("/admin/users");
    return response.data;
}

export async function createUser(data) {
    const response = await client.post("/admin/users", data);
    return response.data;
}

export async function getUnits(unitType) {
    const response = await client.get(`/stations/units?unit_type=${unitType}`);
  return response.data;
}

export async function resetUserPassword(firefighterNumber) {
    const response = await client.post(`/admin/users/${firefighterNumber}/reset-password`);
    return response.data;
}

export async function deleteUser(firefighterNumber) {
    const response = await client.delete(`/admin/users/${firefighterNumber}`);
    return response.data;
}

export async function getUserLeaves(userId) {
    const response = await client.get(`/admin/users/${userId}/leave`);
    return response.data;
}

export async function startUserLeave(userId, data) {
    const response = await client.post(`/admin/users/${userId}/leave`, data);
    return response.data;
}

export async function endUserLeave(userId, data) {
    const response = await client.patch(`/admin/users/${userId}/leave/return`, data);
    return response.data;
}