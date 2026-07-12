import client from "./client";

export async function getMySchedule(year, month) {
  const response = await client.get("/schedules/my", { params: { year, month } });
  return response.data;
}

export async function upsertMySchedule(date, data) {
  const response = await client.put(`/schedules/my/${date}`, data);
  return response.data;
}
