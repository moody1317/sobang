export const PLACE_CATEGORIES = [
  { code: 'MT1', label: '대형마트' },
  { code: 'CS2', label: '편의점' },
  { code: 'PS3', label: '어린이집/유치원' },
  { code: 'SC4', label: '학교' },
  { code: 'AC5', label: '학원' },
  { code: 'PK6', label: '주차장' },
  { code: 'OL7', label: '주유소/충전소' },
  { code: 'SW8', label: '지하철역' },
  { code: 'CT1', label: '문화시설' },
  { code: 'AG2', label: '부동산' },
  { code: 'PO3', label: '공공기관' },
  { code: 'AT4', label: '관광명소' },
  { code: 'AD5', label: '숙박' },
  { code: 'FD6', label: '음식점' },
  { code: 'CE7', label: '카페' },
  { code: 'HP8', label: '병원' },
  { code: 'PM9', label: '약국' },
];

export function searchNearbyPlaces(kakao, location, radius) {
  const places = new kakao.maps.services.Places();

  const searches = PLACE_CATEGORIES.map(
    (cat) =>
      new Promise((resolve) => {
        places.categorySearch(
          cat.code,
          (result, status, pagination) => {
            if (status === kakao.maps.services.Status.OK) {
              resolve({ ...cat, count: pagination?.totalCount ?? result.length });
            } else {
              resolve({ ...cat, count: 0 });
            }
          },
          { location, radius, sort: kakao.maps.services.SortBy.DISTANCE }
        );
      })
  );

  return Promise.all(searches);
}
