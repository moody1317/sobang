import client from "./client";

export async function getStatisticsOverview(year) {
  const response = await client.get("/statistics/overview", { params: year ? { year } : {} });
  return response.data;
}