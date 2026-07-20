import client from "./client";

export async function getRiskMapDongs() {
  const response = await client.get("/risk-map/dongs");
  return response.data;
}

export async function getDongRiskHistory(adminCode, weeks = 8) {
  const response = await client.get(`/risk-map/dongs/${adminCode}/history`, { params: { weeks } });
  return response.data;
}