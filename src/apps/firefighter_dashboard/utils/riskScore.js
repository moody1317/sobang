export const LEVEL_CLASS = { 위험: 'danger', 경계: 'caution', 주의: 'warning', 안전: 'safe' };
export const LEVEL_BY_KEY = { danger: '위험', caution: '경계', warning: '주의', safe: '안전' };

export const BREAKDOWN_LABELS = {
  forest: '산불위험지수',
  target: '소방대상물위험',
  weather: '기상',
  earthquake: '지진',
  fire: '화재이력',
  ems: '구급이력',
  mountain: '산악이력',
  death: '사망',
  injury: '부상',
  damage: '재산피해',
  elderly_bonus: '고령인구가산',
};

export function resolveLevel(score) {
  if (score >= 60) return 'danger';
  if (score >= 40) return 'caution';
  if (score >= 20) return 'warning';
  return 'safe';
}

export function topBreakdownLabel(breakdown) {
  if (!breakdown) return null;
  const [topKey] = Object.entries(breakdown).sort((a, b) => b[1] - a[1])[0] ?? [];
  return BREAKDOWN_LABELS[topKey] ?? topKey ?? null;
}