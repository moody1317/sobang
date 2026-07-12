import client from "./client";

export async function getInspections(status) {
  const response = await client.get("/inspections", { params: status ? { status } : {} });
  return response.data;
}

export async function createInspection(data) {
  const response = await client.post("/inspections", data);
  return response.data;
}

export async function startInspection(id) {
  const response = await client.patch(`/inspections/${id}/start`);
  return response.data;
}

export async function completeInspection(id, data) {
  const response = await client.patch(`/inspections/${id}/complete`, data);
  return response.data;
}

export async function getMyJurisdictions() {
  const response = await client.get("/jurisdictions/my");
  return response.data;
}