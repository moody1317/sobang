let loadingPromise = null;

export function loadKakaoMap() {
  if (window.kakao?.maps) {
    return Promise.resolve(window.kakao);
  }

  if (loadingPromise) {
    return loadingPromise;
  }

  loadingPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${import.meta.env.VITE_KAKAO_MAP_KEY}&autoload=false`;
    script.onload = () => window.kakao.maps.load(() => resolve(window.kakao));
    script.onerror = reject;
    document.head.appendChild(script);
  });

  return loadingPromise;
}
