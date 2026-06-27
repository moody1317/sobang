import DashboardLayout from '../layouts/dashboardlayout';
import './data.css';

const WEIGHTS = [
  { label: '출동 빈도',       pct: 35, desc: '최근 3년 화재·구급·구조 출동 건수 (유형별 가중)' },
  { label: '사고 유형 비중',  pct: 25, desc: '인명피해를 동반한 중대사고의 비율' },
  { label: '시간대 가중치',   pct: 20, desc: '야간·심야 등 대응이 어려운 시간대 출동 비중' },
  { label: '기상 가중치',     pct: 10, desc: '건조특보·강풍 등 계절적 위험 요인 (보조)' },
  { label: '건물 위험 가중치', pct: 10, desc: '대형화재취약대상 비율, 소방시설 미비율 (보조)' },
];

const STEPS = [
  '변수별 값을 0-1로 정규화',
  '가중치를 적용해 가중합 산출',
  '0-100 스케일로 변환해 등급화',
];

const GRADES = [
  { label: '안전', color: 'var(--color-risk-safe)',    range: '0 – 39' },
  { label: '주의', color: 'var(--color-risk-warning)', range: '40 – 59' },
  { label: '경계', color: 'var(--color-risk-caution)', range: '60 – 79' },
  { label: '위험', color: 'var(--color-risk-danger)',  range: '80 – 100' },
];

const SOURCES = [
  {
    name: '산악사고·화재 구조출동 현황',
    provider: '소방안전 빅데이터 플랫폼',
    desc: '지역·건물 단위 출동 빈도의 메인 원자료',
  },
  {
    name: '소방청_화재정보서비스',
    provider: '공공데이터포털 / 소방청',
    desc: '발생일자별 화재 발생·피해현황으로 출동 데이터 보강',
  },
  {
    name: '소방청_구급통계서비스',
    provider: '공공데이터포털 / 소방청',
    desc: '구급 출동 통계로 사고 유형 다양성 확보',
  },
  {
    name: '소방청_특정소방대상물정보서비스',
    provider: '공공데이터포털 / 소방청',
    desc: '대형화재취약대상 여부로 건물 단위 가중치 보강',
  },
  {
    name: '소방청_소방시설정보서비스',
    provider: '공공데이터포털 / 소방청',
    desc: '소방시설 완비 여부를 스코어 보정 변수로 활용',
  },
  {
    name: '기상청 단기예보 / 초단기실황 API',
    provider: '기상청 / 공공데이터포털',
    desc: '계절·시간별 기상 조건을 가중치 변수로 반영',
  },
];

function DataPage() {
  return (
    <div className="data">
      <div className="data-hero">
        <h2 className="data-hero-title">통합 위험 스코어는 이렇게 만들어집니다</h2>
        <p className="data-hero-desc">
          소방 출동 데이터를 중심으로 여러 위험 변수를 정규화한 뒤, 변수별 가중치를 적용해 합산합니다.
          결과는 행정구역별 <strong>0-100점</strong>의 단일 위험 스코어로 표현되며, 점수 산출 근거를
          함께 제공해 설명 가능성을 확보합니다.
        </p>
      </div>

      <div className="data-grid">
        <div className="data-card">
          <h3 className="data-card-title">변수별 가중치</h3>
          <div className="data-weights">
            {WEIGHTS.map((w) => (
              <div key={w.label} className="data-weight-item">
                <div className="data-weight-row">
                  <span className="data-weight-label">{w.label}</span>
                  <span className="data-weight-pct">{w.pct}%</span>
                </div>
                <div className="data-bar-track">
                  <div className="data-bar-fill" style={{ width: `${w.pct}%` }} />
                </div>
                <span className="data-weight-desc">{w.desc}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="data-side">
          <div className="data-card">
            <h3 className="data-card-title">산출 방식</h3>
            <div className="data-steps">
              {STEPS.map((s, i) => (
                <div key={i} className="data-step">
                  <div className="data-step-num">{i + 1}</div>
                  <span className="data-step-text">{s}</span>
                </div>
              ))}
            </div>
            <div className="data-formula">
              score = Σ (w<sub>i</sub> × norm(x<sub>i</sub>)) × 100
            </div>
          </div>

          <div className="data-card">
            <h3 className="data-card-title">등급 기준</h3>
            <div className="data-grades">
              {GRADES.map((g) => (
                <div key={g.label} className="data-grade-item">
                  <div className="data-grade-left">
                    <span className="data-grade-dot" style={{ background: g.color }} />
                    <span className="data-grade-label">{g.label}</span>
                  </div>
                  <span className="data-grade-range">{g.range}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="data-card data-sources-card">
        <div className="data-sources-header">
          <h3 className="data-card-title">데이터 출처</h3>
          <p className="data-sources-sub">공공데이터포털·소방청·기상청의 공개 데이터를 활용합니다</p>
        </div>
        <div className="data-sources">
          {SOURCES.map((s) => (
            <div key={s.name} className="data-source-row">
              <span className="data-source-name">{s.name}</span>
              <span className="data-source-provider">{s.provider}</span>
              <span className="data-source-desc">{s.desc}</span>
            </div>
          ))}
        </div>
        <div className="data-notice">
          <i className="bi bi-info-circle" />
          <span>
            <strong>MVP 제외 범위</strong> · 길찾기 API(Kakao/Naver), 국가교통정보센터(ITS) 도로 정보 등
            접근성 분석 항목은 본 버전에서 제외되며, 향후 확장 과제로 분류됩니다.
          </span>
        </div>
      </div>
    </div>
  );
}

function DataPagePage() {
  return (
    <DashboardLayout>
      <DataPage />
    </DashboardLayout>
  );
}

export default DataPagePage;
