import client from "./client";

export async function getUsers() {
  const response = await client.get("/admin/users");
  return response.data;
}

export async function bulkRegisterEducation(title, date) {
  const response = await client.post("/admin/schedules/bulk-education", { title, date });
  return response.data;
}
