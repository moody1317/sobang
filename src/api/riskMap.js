import client from "./client";

export async function getRiskMapDongs() {
  const response = await client.get("/risk-map/dongs");
  return response.data;
}