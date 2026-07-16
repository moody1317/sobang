import { useState, useEffect, useMemo, useCallback } from 'react';
import DashboardLayout from '../layouts/dashboardlayout';
import { useUser } from '../contexts/usercontext';
import { getMySchedule, upsertMySchedule } from '../../../api/schedule';
import TrainingBulkAddModal from './trainingBulkAdd';
import './schedule.css';

const WORK_TYPES = [
  { key: '주간', label: '주간 근무', color: 'blue' },
  { key: '야간', label: '야간 근무', color: 'purple' },
  { key: '비번', label: '비번/휴무', color: 'gray' },
];

const DAY_LABELS = ['월', '화', '수', '목', '금', '토', '일'];
const WEEKDAY_NAMES = ['일', '월', '화', '수', '목', '금', '토'];

function dateKey(year, month, day) {
  return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

const DEFAULT_DAY = { workType: '주간', start: '09:00', end: '18:00', patrol: false, training: false, records: 0 };

function toEntry(item) {
  return {
    workType: item.shift_type,
    start: item.start_time?.slice(0, 5) ?? DEFAULT_DAY.start,
    end: item.end_time?.slice(0, 5) ?? DEFAULT_DAY.end,
    patrol: item.is_patrol,
    training: item.is_education,
    records: 0,
  };
}

const realToday = new Date();
const INIT_YEAR  = realToday.getFullYear();
const INIT_MONTH = realToday.getMonth();
const INIT_DAY   = realToday.getDate();

function SchedulePage() {
  const user = useUser();
  const isAdmin = user?.rank === '관리자';

  const todayKey = dateKey(INIT_YEAR, INIT_MONTH, INIT_DAY);

  const [viewYear,  setViewYear]  = useState(INIT_YEAR);
  const [viewMonth, setViewMonth] = useState(INIT_MONTH);
  const [selectedDay, setSelectedDay] = useState(INIT_DAY);
  const [schedule, setSchedule]   = useState({});
  const [showTrainingModal, setShowTrainingModal] = useState(false);

  const fetchSchedule = useCallback(async () => {
    const items = await getMySchedule(viewYear, viewMonth + 1);
    const data = {};
    for (const item of items) data[item.date] = toEntry(item);
    setSchedule(data);
  }, [viewYear, viewMonth]);

  useEffect(() => {
    fetchSchedule();
  }, [fetchSchedule]);

  const daysInMonth  = new Date(viewYear, viewMonth + 1, 0).getDate();
  const firstWeekday = new Date(viewYear, viewMonth, 1).getDay();
  const offset       = (firstWeekday + 6) % 7; // Monday-first

  const selKey  = dateKey(viewYear, viewMonth, selectedDay);
  const dayData = schedule[selKey] ?? DEFAULT_DAY;

  const selDate    = new Date(viewYear, viewMonth, selectedDay);
  const weekdayStr = WEEKDAY_NAMES[selDate.getDay()];

  const summary = useMemo(() => {
    const c = { 주간: 0, 야간: 0, 비번: 0, patrol: 0, training: 0, records: 0 };
    for (let d = 1; d <= daysInMonth; d++) {
      const v = schedule[dateKey(viewYear, viewMonth, d)] ?? DEFAULT_DAY;
      if (v.workType === '주간') c.주간++;
      else if (v.workType === '야간') c.야간++;
      else c.비번++;
      if (v.patrol)   c.patrol++;
      if (v.training) c.training++;
      c.records += v.records;
    }
    return c;
  }, [schedule, viewYear, viewMonth, daysInMonth]);

  function prevMonth() {
    if (viewMonth === 0) { setViewYear(y => y - 1); setViewMonth(11); }
    else setViewMonth(m => m - 1);
    setSelectedDay(1);
  }
  function nextMonth() {
    if (viewMonth === 11) { setViewYear(y => y + 1); setViewMonth(0); }
    else setViewMonth(m => m + 1);
    setSelectedDay(1);
  }

  async function updateDay(patch) {
    const next = { ...dayData, ...patch };
    setSchedule(prev => ({ ...prev, [selKey]: next }));
    await upsertMySchedule(selKey, {
      shift_type: next.workType,
      start_time: next.start,
      end_time: next.end,
      is_patrol: next.patrol,
      is_education: next.training,
    });
  }

  const cells = [
    ...Array(offset).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ];

  return (
    <DashboardLayout>
      <div className="sch">

        <div className="sch-cal-card">

          <div className="sch-cal-header">
            <div className="sch-cal-title-row">
              <span className="sch-cal-title">{viewYear}년 {viewMonth + 1}월</span>
              <div className="sch-cal-nav">
                <button className="sch-nav-btn" onClick={prevMonth}><i className="bi bi-chevron-left" /></button>
                <button className="sch-nav-btn" onClick={nextMonth}><i className="bi bi-chevron-right" /></button>
              </div>
            </div>
            <div className="sch-legend">
              <span className="sch-legend-item"><span className="sch-ldot sch-ldot--blue" />주간 근무</span>
              <span className="sch-legend-item"><span className="sch-ldot sch-ldot--purple" />야간 근무</span>
              <span className="sch-legend-item"><span className="sch-ldot sch-ldot--gray" />비번/휴무</span>
              <span className="sch-legend-item"><i className="bi bi-send sch-licon sch-licon--patrol" />순찰</span>
              <span className="sch-legend-item"><i className="bi bi-mortarboard sch-licon sch-licon--training" />교육</span>
            </div>
          </div>

          <div className="sch-cal-grid">
            {DAY_LABELS.map(l => (
              <div key={l} className="sch-day-label">{l}</div>
            ))}

            {cells.map((day, i) => {
              if (!day) return <div key={`e${i}`} className="sch-cell sch-cell--empty" />;
              const k   = dateKey(viewYear, viewMonth, day);
              const d   = schedule[k] ?? DEFAULT_DAY;
              const wt  = d.workType === '주간' ? 'blue' : d.workType === '야간' ? 'purple' : 'gray';
              const sel = day === selectedDay;
              const tod = k === todayKey;
              return (
                <div
                  key={day}
                  className={`sch-cell${sel ? ' selected' : ''}${tod ? ' today' : ''}`}
                  onClick={() => setSelectedDay(day)}
                >
                  <div className="sch-cell-top">
                    <span className={`sch-cell-date${tod ? ' sch-cell-date--today' : ''}`}>{day}</span>
                    {tod && <span className="sch-today-badge">오늘</span>}
                  </div>
                  <span className={`sch-work-badge sch-work-badge--${wt}`}>
                    {d.workType === '주간' ? '주간' : d.workType === '야간' ? '야간' : '비번'}
                  </span>
                  <div className="sch-cell-acts">
                    {d.records > 0 && (
                      <span className="sch-act-row">
                        <span className="sch-act-dot" />
                        <span className="sch-act-text">기록{d.records}</span>
                      </span>
                    )}
                    {d.patrol && (
                      <span className="sch-act-row">
                        <i className="bi bi-send sch-act-icon sch-act-icon--patrol" />
                      </span>
                    )}
                    {d.training && (
                      <span className="sch-act-row">
                        <i className="bi bi-mortarboard sch-act-icon sch-act-icon--training" />
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="sch-detail">
          <div className="sch-detail-card">
            <div className="sch-detail-date">
              <span className="sch-detail-date-main">{viewMonth + 1}월 {selectedDay}일</span>
              <span className="sch-detail-date-sub">{weekdayStr}요일</span>
            </div>

            <div className="sch-section">
              <div className="sch-section-label">근무 형태</div>
              <div className="sch-work-types">
                {WORK_TYPES.map(({ key, label, color }) => (
                  <button
                    key={key}
                    className={`sch-wt-btn sch-wt-btn--${color}${dayData.workType === key ? ' active' : ''}`}
                    onClick={() => updateDay({ workType: key })}
                  >
                    <span className={`sch-wdot sch-wdot--${color}`} />
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {dayData.workType !== '비번' && (
              <div className="sch-section">
                <div className="sch-section-label">근무 시간</div>
                <div className="sch-time-row">
                  <div className="sch-time-wrap">
                    <input
                      type="time"
                      className="sch-time-input"
                      value={dayData.start}
                      onChange={e => updateDay({ start: e.target.value })}
                    />
                  </div>
                  <span className="sch-time-dash">–</span>
                  <div className="sch-time-wrap">
                    <input
                      type="time"
                      className="sch-time-input"
                      value={dayData.end}
                      onChange={e => updateDay({ end: e.target.value })}
                    />
                  </div>
                </div>
              </div>
            )}

            {dayData.workType !== '비번' && (
              <div className="sch-section">
                <div className="sch-section-label">
                  근무 중 활동
                  <span className="sch-section-hint">근무에 더해 선택</span>
                </div>
                <div className="sch-activities">
                  <button
                    className={`sch-act-btn${dayData.patrol ? ' active' : ''}`}
                    onClick={() => updateDay({ patrol: !dayData.patrol })}
                  >
                    <i className="bi bi-send sch-act-btn-icon sch-act-btn-icon--patrol" />
                    순찰
                  </button>
                  <button
                    className={`sch-act-btn${dayData.training ? ' active' : ''}`}
                    onClick={() => updateDay({ training: !dayData.training })}
                  >
                    <i className="bi bi-mortarboard sch-act-btn-icon sch-act-btn-icon--training" />
                    교육
                  </button>
                </div>
              </div>
            )}

            {isAdmin && (
              <button className="sch-admin-btn" onClick={() => setShowTrainingModal(true)}>
                <i className="bi bi-people" />
                관리자·교육 일괄 등록
              </button>
            )}
          </div>

          <div className="sch-detail-card">
            <div className="sch-section-label sch-section-label--card">이번 달 근무 구성</div>
            <div className="sch-summary-rows">
              <div className="sch-summary-row">
                <span className="sch-summary-left"><span className="sch-ldot sch-ldot--blue" />주간 근무</span>
                <span className="sch-summary-val">{summary.주간}일</span>
              </div>
              <div className="sch-summary-row">
                <span className="sch-summary-left"><span className="sch-ldot sch-ldot--purple" />야간 근무</span>
                <span className="sch-summary-val">{summary.야간}일</span>
              </div>
              <div className="sch-summary-row">
                <span className="sch-summary-left"><span className="sch-ldot sch-ldot--gray" />비번/휴무</span>
                <span className="sch-summary-val">{summary.비번}일</span>
              </div>
            </div>
            <div className="sch-summary-div" />
            <div className="sch-summary-rows">
              <div className="sch-summary-row">
                <span className="sch-summary-left"><i className="bi bi-send sch-licon sch-licon--patrol" />순찰 활동</span>
                <span className="sch-summary-val">{summary.patrol}일</span>
              </div>
              <div className="sch-summary-row">
                <span className="sch-summary-left"><i className="bi bi-mortarboard sch-licon sch-licon--training" />교육 활동</span>
                <span className="sch-summary-val">{summary.training}일</span>
              </div>
            </div>
            <div className="sch-summary-div" />
            <div className="sch-summary-row">
              <span className="sch-summary-left sch-dispatch-label">이번 달 출동 기록</span>
              <span className="sch-summary-val sch-dispatch-val">{summary.records}건</span>
            </div>
          </div>

        </div>
      </div>

      {showTrainingModal && (
        <TrainingBulkAddModal
          viewYear={viewYear}
          viewMonth={viewMonth}
          defaultDay={selectedDay}
          onClose={() => setShowTrainingModal(false)}
          onRegistered={fetchSchedule}
        />
      )}
    </DashboardLayout>
  );
}

export default SchedulePage;
