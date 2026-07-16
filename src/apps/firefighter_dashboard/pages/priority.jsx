import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../layouts/dashboardlayout';
import { getRiskMapDongs } from '../../../api/riskMap';
import { LEVEL_CLASS, LEVEL_BY_KEY, resolveLevel, topBreakdownLabel } from '../utils/riskScore';
import './priority.css';

function inferType(dongNm) {
  if (!dongNm) return '동';
  if (dongNm.endsWith('읍')) return '읍';
  if (dongNm.endsWith('면')) return '면';
  return '동';
}

function PriorityList() {
  const navigate = useNavigate();
  const [dongs, setDongs] = useState([]);
  const [status, setStatus] = useState('loading'); // loading | ready | error

  useEffect(() => {
    let cancelled = false;

    getRiskMapDongs()
      .then((data) => {
        if (cancelled) return;
        setDongs(data);
        setStatus('ready');
      })
      .catch(() => {
        if (!cancelled) setStatus('error');
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const rankedRegions = useMemo(() => {
    return [...dongs]
      .sort((a, b) => b.risk_score - a.risk_score)
      .map((d, i) => ({
        admin_code: d.admin_code,
        name: d.dong_nm,
        type: inferType(d.dong_nm),
        district: d.sigungu_nm,
        level: LEVEL_BY_KEY[resolveLevel(Number(d.risk_score))],
        score: Math.round(Number(d.risk_score) * 10) / 10,
        rank: i + 1,
        total: dongs.length,
        mainFactor: topBreakdownLabel(d.risk_score_breakdown),
        breakdown: d.risk_score_breakdown ?? {},
      }));
  }, [dongs, resolveLevel]);

  return (
    <div className="priority">
      <div className="priority-warn">
        <i className="bi bi-exclamation-triangle-fill priority-warn-icon" />
        <span>
          위험 스코어가 높은 구역일수록 출동 가능성이 큽니다.
          상위 구역부터 <strong>점검·순찰 우선순위</strong>를 배정하세요.
        </span>
      </div>

      <div className="priority-card">
        <div className="priority-head">
          <span className="priority-col priority-col--rank">순위</span>
          <span className="priority-col priority-col--region">행정구역</span>
          <span className="priority-col priority-col--score">위험 등급 · 스코어</span>
          <span className="priority-col priority-col--type">주요 위험요인</span>
          <span className="priority-col priority-col--action" />
        </div>

        {status === 'loading' && <p className="priority-empty">불러오는 중입니다</p>}
        {status === 'error' && <p className="priority-empty">데이터를 불러오지 못했습니다</p>}
        {status === 'ready' && rankedRegions.length === 0 && (
          <p className="priority-empty">표시할 관할동 데이터가 없습니다</p>
        )}

        {rankedRegions.map((region) => {
          const levelCls = LEVEL_CLASS[region.level] ?? 'safe';
          return (
            <div key={region.admin_code} className="priority-row">
              <span className={`priority-col priority-col--rank priority-rank${region.rank <= 3 ? ' top' : ''}`}>
                {region.rank}
              </span>

              <div className="priority-col priority-col--region">
                <span className="priority-region-name">{region.name}</span>
                <span className="priority-region-sub">{region.type} · {region.district}</span>
              </div>

              <div className="priority-col priority-col--score">
                <div className="priority-score-row">
                  <span className={`priority-level-badge priority-level-badge--${levelCls}`}>{region.level}</span>
                  <span className={`priority-score-num priority-score-num--${levelCls}`}>{region.score}</span>
                </div>
                <div className="priority-bar-track">
                  <div className={`priority-bar priority-bar--${levelCls}`} style={{ width: `${region.score}%` }} />
                </div>
              </div>

              <span className="priority-col priority-col--type priority-type-text">
                {region.mainFactor ?? '-'}
              </span>

              <div className="priority-col priority-col--action">
                <button
                  className="priority-detail-btn"
                  onClick={() => navigate('/dashboard/map', { state: { region } })}
                >
                  상세
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function PriorityPage() {
  return (
    <DashboardLayout>
      <PriorityList />
    </DashboardLayout>
  );
}

export default PriorityPage;