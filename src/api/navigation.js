import client from './client';

export async function getRoute(originLat, originLng, destLat, destLng) {
  const response = await client.get('/navigation/route', {
    params: {
      origin_lat: originLat,
      origin_lng: originLng,
      dest_lat: destLat,
      dest_lng: destLng,
    },
  });
  return response.data;
}
