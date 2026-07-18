import DashboardLayout from '../layouts/dashboardlayout';
import './data.css';

const WEIGHTS = [
  { label: '산불위험지수',     pct: 15,   desc: '구역 산불위험지수(0-100)를 스코어에 그대로 반영' },
  { label: '소방대상물위험',   pct: 15,   desc: '대형화재취약대상 수를 구역 간 min-max 정규화' },
  { label: '화재이력',         pct: 15,   desc: '화재 출동 건수를 구역 간 min-max 정규화' },
  { label: '기상',             pct: 12.5, desc: '건조·강풍 등 활성 특보의 가중치 합산 (최대치 캡)' },
  { label: '지진',             pct: 12.5, desc: '최근 지진 발생 영향도 (최대치 캡)' },
  { label: '구급이력',         pct: 10,   desc: '구급 출동 건수를 구역 간 min-max 정규화' },
  { label: '사망',             pct: 7,    desc: '화재 사망자 수 합계를 구역 간 min-max 정규화' },
  { label: '산악이력',         pct: 5,    desc: '산악사고 건수를 구역 간 min-max 정규화' },
  { label: '부상',             pct: 4,    desc: '화재 부상자 수 합계를 구역 간 min-max 정규화' },
  { label: '재산피해',         pct: 4,    desc: '화재 재산피해액 합계를 구역 간 min-max 정규화' },
];

const STEPS = [
  '1단계 — 관할구역별로 변수 원자료 집계 (출동 건수·인명피해/재산피해 합계·산불위험지수 등)',
  '변수 성격별로 정규화 — 출동·피해 건수는 관할구역 간 min-max, 기상·지진은 활성 특보/최근성 기준으로 캡 적용',
  '정규화 값에 배점을 곱해 합산 → 관할구역 위험 스코어 산출 (100 초과 시 100으로 clip)',
  '2단계 — 행정동은 관할구역 스코어를 인구 비율로 배분, 소방대상물위험은 동 단위로 재계산하고 고령인구비율 가산(최대 5점)을 더함',
];

const GRADES = [
  { label: '안전', color: 'var(--color-risk-safe)',    range: '0 – 19' },
  { label: '주의', color: 'var(--color-risk-warning)', range: '20 – 49' },
  { label: '경계', color: 'var(--color-risk-caution)', range: '50 – 79' },
  { label: '위험', color: 'var(--color-risk-danger)',  range: '80 – 100' },
];

const SOURCE_GROUPS = [
  {
    title: '위험 스코어 산정에 사용',
    items: [
      {
        name: '화재 출동 정보',
        provider: '소방안전 빅데이터 플랫폼 (bigdata-119.kr)',
        desc: '화재이력·사망·부상·재산피해 변수의 원자료',
      },
      {
        name: '구급 출동 정보',
        provider: '소방안전 빅데이터 플랫폼 (bigdata-119.kr)',
        desc: '구급이력 변수의 원자료',
      },
      {
        name: '소방대상물 정보',
        provider: '소방안전 빅데이터 플랫폼 (bigdata-119.kr)',
        desc: '대형화재취약대상 수로 소방대상물위험 변수 산출',
      },
      {
        name: '산악사고 현황',
        provider: '소방청 (정적 CSV, 2024.12.31 기준)',
        desc: '산악이력 변수의 원자료',
      },
      {
        name: '산불위험지수',
        provider: '산림청 / 공공데이터포털',
        desc: '구역별 산불위험지수를 정규화 없이 그대로 반영',
      },
      {
        name: '기상특보 (주의보·경보)',
        provider: '기상청 / 공공데이터포털',
        desc: '건조·강풍 등 활성 특보 가중치를 기상 변수에 반영',
      },
      {
        name: '지진 정보',
        provider: '기상청 / 공공데이터포털',
        desc: '최근 지진 발생 영향도를 지진 변수에 반영',
      },
    ],
  },
  {
    title: '스코어 배분 · 인프라에 사용',
    items: [
      {
        name: '행정동 인구 (연령·성별)',
        provider: '공공데이터포털',
        desc: '관할구역 스코어를 행정동에 인구비율로 배분, 고령인구가산에도 사용',
      },
      {
        name: '행정동 경계 GeoJSON',
        provider: 'vuski/admdongkor (오픈소스)',
        desc: '행정동 지도 시각화용 경계 데이터',
      },
      {
        name: '관할구역 경계',
        provider: 'VWorld WFS API',
        desc: '소방서 관할구역 지오메트리 생성',
      },
      {
        name: '전국 소방서 위치',
        provider: '공공데이터포털',
        desc: '산악사고를 관할 소방서에 매칭할 때 사용',
      },
    ],
  },
  {
    title: '스코어 외 다른 화면 기능에 사용',
    items: [
      {
        name: '구급환자 이송정보',
        provider: '공공데이터포털',
        desc: '통계 페이지의 시간대별 구급 출동 분포에 사용 (스코어 무관)',
      },
      {
        name: 'Kakao Mobility Directions',
        provider: 'Kakao',
        desc: '순찰 앱 실도로 경로 안내에 사용 (스코어 무관)',
      },
    ],
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
              관할구역 = min(100, Σ w<sub>i</sub> × norm(x<sub>i</sub>))
              <br />
              행정동 = min(100, Σ w<sub>k</sub> × norm(x<sub>k</sub>) × popRatio + 고정항 + 고령가산)
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
          {SOURCE_GROUPS.map((group) => (
            <div key={group.title} className="data-source-group">
              <h4 className="data-source-group-title">{group.title}</h4>
              {group.items.map((s) => (
                <div key={s.name} className="data-source-row">
                  <span className="data-source-name">{s.name}</span>
                  <span className="data-source-provider">{s.provider}</span>
                  <span className="data-source-desc">{s.desc}</span>
                </div>
              ))}
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
