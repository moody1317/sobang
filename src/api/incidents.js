import client from "./client";

export async function getActiveIncidents() {
  const response = await client.get("/incidents/active");
  return response.data;
}

export async function updateIncidentStatus(incidentId, newStatus, isFalseAlarm) {
  const response = await client.patch(`/incidents/${incidentId}/status`, null, {
    params: {
      new_status: newStatus,
      ...(isFalseAlarm !== undefined ? { is_false_alarm: isFalseAlarm } : {}),
    },
  });
  return response.data;
}

export async function getMyDispatchDates(year, month) {
  const response = await client.get("/incidents/dispatches/my", { params: { year, month } });
  return response.data;
}

export async function confirmDispatch(incidentId) {
  const response = await client.post(`/incidents/${incidentId}/dispatch`);
  return response.data;
}

export async function completeReturn(incidentId, data) {
  const response = await client.patch(`/incidents/${incidentId}/dispatch/return`, data);
  return response.data;
}