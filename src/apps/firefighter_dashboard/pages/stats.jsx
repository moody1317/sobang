import DashboardLayout from '../layouts/dashboardlayout';
import './stats.css';

const MONTHLY_DATA = [
  { month: '1월',  count: 448 },
  { month: '2월',  count: 402 },
  { month: '3월',  count: 386 },
  { month: '4월',  count: 418 },
  { month: '5월',  count: 344 },
  { month: '6월',  count: 330 },
  { month: '7월',  count: 372 },
  { month: '8월',  count: 388 },
  { month: '9월',  count: 340 },
  { month: '10월', count: 356 },
  { month: '11월', count: 392 },
  { month: '12월', count: 447 },
];

const TYPE_DATA = [
  { label: '화재', count: 982,  pct: 21, color: 'var(--color-risk-danger)' },
  { label: '구급', count: 2772, pct: 60, color: 'var(--color-blue)' },
  { label: '구조', count: 675,  pct: 15, color: 'var(--color-risk-caution)' },
  { label: '산악', count: 196,  pct: 4,  color: 'var(--color-risk-safe)' },
];

const TIME_DATA = [
  { label: '심야', sub: '00-06', pct: 18 },
  { label: '오전', sub: '06-12', pct: 24 },
  { label: '오후', sub: '12-18', pct: 29 },
  { label: '저녁', sub: '18-24', pct: 29 },
];

const SUMMARY = [
  {
    label: '누적 출동 (최근 1년)',
    render: () => (
      <><span className="stats-kpi-num">4,625</span><span className="stats-kpi-unit">건</span></>
    ),
  },
  {
    label: '평균 위험 스코어',
    render: () => (
      <><span className="stats-kpi-num">64</span><span className="stats-kpi-unit">/100</span></>
    ),
  },
  {
    label: '위험 등급 구역',
    render: () => (
      <><span className="stats-kpi-num stats-kpi-num--danger">3</span><span className="stats-kpi-unit">/15곳</span></>
    ),
  },
  {
    label: '최다 출동 유형',
    render: () => (
      <><span className="stats-kpi-num">구급</span><span className="stats-kpi-unit">64%</span></>
    ),
  },
];

function Stats() {
  const maxMonthly = Math.max(...MONTHLY_DATA.map((d) => d.count));
  const maxTimePct = Math.max(...TIME_DATA.map((d) => d.pct));

  return (
    <DashboardLayout>
      <div className="stats">

        <div className="stats-kpi-grid">
          {SUMMARY.map((s) => (
            <div key={s.label} className="stats-kpi-card">
              <span className="stats-kpi-label">{s.label}</span>
              <div className="stats-kpi-value">{s.render()}</div>
            </div>
          ))}
        </div>

        <div className="stats-card">
          <div className="stats-card-header">
            <span className="stats-card-title">월별 출동 추이</span>
            <span className="stats-card-sub">겨울철·봄철 건조기에 출동이 집중됩니다</span>
          </div>
          <div className="stats-month-chart">
            {MONTHLY_DATA.map(({ month, count }) => (
              <div key={month} className="stats-month-col">
                <span className="stats-month-count">{count}</span>
                <div className="stats-month-bar-track">
                  <div
                    className="stats-month-bar"
                    style={{ height: `${(count / maxMonthly) * 100}%` }}
                  />
                </div>
                <span className="stats-month-label">{month}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="stats-bottom-grid">
          <div className="stats-card">
            <div className="stats-card-header">
              <span className="stats-card-title">사고 유형별 출동 구성</span>
            </div>
            <div className="stats-type-list">
              {TYPE_DATA.map(({ label, count, pct, color }) => (
                <div key={label} className="stats-type-row">
                  <div className="stats-type-meta">
                    <span className="stats-type-dot" style={{ background: color }} />
                    <span className="stats-type-label">{label}</span>
                    <span className="stats-type-stat">{count.toLocaleString()}건 · {pct}%</span>
                  </div>
                  <div className="stats-type-bar-track">
                    <div className="stats-type-bar" style={{ width: `${pct}%`, background: color }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="stats-card">
            <div className="stats-card-header">
              <span className="stats-card-title">시간대별 출동 분포</span>
              <span className="stats-card-sub">저녁·심야 시간대 대응 부담이 큽니다</span>
            </div>
            <div className="stats-time-chart">
              {TIME_DATA.map(({ label, sub, pct }) => (
                <div key={label} className="stats-time-col">
                  <span className="stats-time-pct">{pct}%</span>
                  <div className="stats-time-bar-track">
                    <div
                      className="stats-time-bar"
                      style={{ height: `${(pct / maxTimePct) * 100}%` }}
                    />
                  </div>
                  <span className="stats-time-label">{label}</span>
                  <span className="stats-time-sub">{sub}</span>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </DashboardLayout>
  );
}

export default Stats;
