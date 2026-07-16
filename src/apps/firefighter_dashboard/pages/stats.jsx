import { useEffect, useMemo, useState } from 'react';
import DashboardLayout from '../layouts/dashboardlayout';
import { getStatisticsOverview } from '../../../api/statistics';
import './stats.css';

const TYPE_COLOR = {
  화재: 'var(--color-risk-danger)',
  구급: 'var(--color-blue)',
  산악: 'var(--color-risk-safe)',
};

const TIME_SUB = { 심야: '00-06', 오전: '06-12', 오후: '12-18', 저녁: '18-24' };

function formatMonthLabel(yyyymm) {
  if (!yyyymm || yyyymm.length !== 6) return yyyymm;
  return `${Number(yyyymm.slice(4, 6))}월`;
}

function formatPct(ratio) {
  return Math.round((ratio ?? 0) * 100);
}

function Stats() {
  const [year, setYear] = useState(new Date().getFullYear());
  const [data, setData] = useState(null);
  const [status, setStatus] = useState('loading'); // loading | ready | error

  useEffect(() => {
    let cancelled = false;
    setStatus('loading');

    getStatisticsOverview(year)
      .then((result) => {
        if (cancelled) return;
        setData(result);
        setStatus('ready');
      })
      .catch(() => {
        if (!cancelled) setStatus('error');
      });

    return () => {
      cancelled = true;
    };
  }, [year]);

  const maxMonthly = useMemo(() => {
    if (!data?.monthly_trend?.length) return 1;
    return Math.max(...data.monthly_trend.map((d) => d.count));
  }, [data]);

  const maxTimePct = useMemo(() => {
    if (!data?.hourly_distribution?.length) return 1;
    return Math.max(...data.hourly_distribution.map((d) => formatPct(d.ratio)), 1);
  }, [data]);

  const isLoading = status === 'loading';

  return (
    <DashboardLayout>
      <div className="stats">
        <div className="stats-year-row">
          <button className="stats-year-btn" onClick={() => setYear((y) => y - 1)}>
            <i className="bi bi-chevron-left" />
          </button>
          <span className="stats-year-label">{year}년</span>
          <button
            className="stats-year-btn"
            onClick={() => setYear((y) => y + 1)}
            disabled={year >= new Date().getFullYear()}
          >
            <i className="bi bi-chevron-right" />
          </button>
          {data?.is_fallback_year && (
            <span className="stats-year-fallback-note">
              {year}년 데이터가 아직 없어 {data.year}년 데이터를 표시하고 있습니다
            </span>
          )}
        </div>

        {status === 'error' && <p className="stats-empty">통계를 불러오지 못했습니다</p>}

        <div className="stats-kpi-grid">
          <div className="stats-kpi-card">
            <span className="stats-kpi-label">누적 출동</span>
            <div className="stats-kpi-value">
              <span className="stats-kpi-num">{isLoading ? '—' : data?.total_dispatches ?? 0}</span>
              <span className="stats-kpi-unit">건</span>
            </div>
          </div>

          <div className="stats-kpi-card">
            <span className="stats-kpi-label">평균 위험 스코어</span>
            <div className="stats-kpi-value">
              {data?.avg_risk_score != null ? (
                <>
                  <span className="stats-kpi-num">{data.avg_risk_score}</span>
                  <span className="stats-kpi-unit">/100</span>
                </>
              ) : (
                <span className="stats-kpi-num stats-kpi-num--muted">{isLoading ? '—' : '데이터 없음'}</span>
              )}
            </div>
          </div>

          <div className="stats-kpi-card">
            <span className="stats-kpi-label">위험 등급 구역</span>
            <div className="stats-kpi-value">
              {data?.high_risk_dong_count != null ? (
                <>
                  <span className="stats-kpi-num stats-kpi-num--danger">{data.high_risk_dong_count}</span>
                  <span className="stats-kpi-unit">/{data.total_dong_count}곳</span>
                </>
              ) : (
                <span className="stats-kpi-num stats-kpi-num--muted">{isLoading ? '—' : '데이터 없음'}</span>
              )}
            </div>
          </div>

          <div className="stats-kpi-card">
            <span className="stats-kpi-label">최다 출동 유형</span>
            <div className="stats-kpi-value">
              {data?.most_frequent_type ? (
                <>
                  <span className="stats-kpi-num">{data.most_frequent_type.type}</span>
                  <span className="stats-kpi-unit">{formatPct(data.most_frequent_type.ratio)}%</span>
                </>
              ) : (
                <span className="stats-kpi-num stats-kpi-num--muted">{isLoading ? '—' : '데이터 없음'}</span>
              )}
            </div>
          </div>
        </div>

        <div className="stats-card">
          <div className="stats-card-header">
            <span className="stats-card-title">월별 출동 추이</span>
            <span className="stats-card-sub">데이터가 집계된 달만 표시됩니다</span>
          </div>
          {data?.monthly_trend?.length ? (
            <div className="stats-month-chart">
              {data.monthly_trend.map(({ month, count }) => (
                <div key={month} className="stats-month-col">
                  <span className="stats-month-count">{count}</span>
                  <div className="stats-month-bar-track">
                    <div className="stats-month-bar" style={{ height: `${(count / maxMonthly) * 100}%` }} />
                  </div>
                  <span className="stats-month-label">{formatMonthLabel(month)}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="stats-empty">{isLoading ? '불러오는 중입니다' : '표시할 월별 데이터가 없습니다'}</p>
          )}
        </div>

        <div className="stats-bottom-grid">
          <div className="stats-card">
            <div className="stats-card-header">
              <span className="stats-card-title">사고 유형별 출동 구성</span>
            </div>
            {data?.type_breakdown?.length ? (
              <div className="stats-type-list">
                {data.type_breakdown.map(({ type, count, ratio }) => (
                  <div key={type} className="stats-type-row">
                    <div className="stats-type-meta">
                      <span className="stats-type-dot" style={{ background: TYPE_COLOR[type] }} />
                      <span className="stats-type-label">{type}</span>
                      <span className="stats-type-stat">{count.toLocaleString()}건 · {formatPct(ratio)}%</span>
                    </div>
                    <div className="stats-type-bar-track">
                      <div
                        className="stats-type-bar"
                        style={{ width: `${formatPct(ratio)}%`, background: TYPE_COLOR[type] }}
                      />
                    </div>
                    {data.type_breakdown_notes?.[type] && (
                      <span className="stats-type-note">{data.type_breakdown_notes[type]}</span>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="stats-empty">{isLoading ? '불러오는 중입니다' : '표시할 데이터가 없습니다'}</p>
            )}
          </div>

          <div className="stats-card">
            <div className="stats-card-header">
              <span className="stats-card-title">시간대별 출동 분포</span>
            </div>
            {data?.hourly_distribution?.length ? (
              <div className="stats-time-chart">
                {data.hourly_distribution.map(({ slot, ratio }) => (
                  <div key={slot} className="stats-time-col">
                    <span className="stats-time-pct">{formatPct(ratio)}%</span>
                    <div className="stats-time-bar-track">
                      <div
                        className="stats-time-bar"
                        style={{ height: `${(formatPct(ratio) / maxTimePct) * 100}%` }}
                      />
                    </div>
                    <span className="stats-time-label">{slot}</span>
                    <span className="stats-time-sub">{TIME_SUB[slot]}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="stats-empty">{isLoading ? '불러오는 중입니다' : '표시할 데이터가 없습니다'}</p>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

export default Stats;