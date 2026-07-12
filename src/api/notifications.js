import client from "./client";

export async function getNotifications(params = {}) {
    const response = await client.get("/notifications", { params });
    return response.data;
}

export async function getUnreadNotificationCount() {
    const response = await client.get("/notifications/unread-count");
    return response.data;
}

export async function markNotificationRead(notificationId) {
    const response = await client.patch(`/notifications/${notificationId}/read`);
    return response.data;
}
