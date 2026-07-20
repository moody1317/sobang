import client from "./client";

export async function getVehicles() {
  const response = await client.get("/admin/vehicles");
  return response.data;
}

export async function createVehicle(data) {
  const response = await client.post("/admin/vehicles", data);
  return response.data;
}

export async function updateVehicleCount(vehicleId, count) {
  const response = await client.patch(`/admin/vehicles/${vehicleId}`, { count });
  return response.data;
}

export async function deleteVehicle(vehicleId) {
  const response = await client.delete(`/admin/vehicles/${vehicleId}`);
  return response.data;
}
