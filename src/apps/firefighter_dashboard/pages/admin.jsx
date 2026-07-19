import { useState, useEffect, useCallback } from 'react';
import { useUser } from '../contexts/userHooks';
import DashboardLayout from '../layouts/dashboardlayout';
import client from '../../../api/client';
import { getStationUsers, createUser, getUnits, resetUserPassword } from '../../../api/auth';
import './admin.css';

const RANKS = ['소방사', '소방교', '소방장', '소방위'];

const UNIT_TYPES = ['본서', '안전센터', '구급대', '항공대', '특수대응단', '지역대', '119구조대'];
const FACILITY_UNIT_TYPES = ['안전센터', '지역대', '119구조대'];
const DEPARTMENTS = ['소방행정과', '재난대응과', '예방안전과', '현장대응단'];

function AddModal({ onClose, onCreated }) {
  const user = useUser();
  const [form, setForm] = useState({
    name: '',
    email: '',
    phone_number: '',
    rank: '소방사',
    unit_type: '본서',
    safety_center_id: null,
    department: null,
  });

  const [safetyCenters, setSafetyCenters] = useState([]);
  const [centersLoading, setCentersLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  function set(key) {
    return (e) => {
      setForm((prev) => ({ ...prev, [key]: e.target.value }));
      setErrors((prev) => ({ ...prev, [key]: undefined }));
    };
  }

  async function handleUnitTypeChange(type) {
    setForm((prev) => ({ ...prev, unit_type: type, safety_center_id: null, department: null }));
    if (FACILITY_UNIT_TYPES.includes(type)) {
      setCentersLoading(true);
      setSafetyCenters([]);
      try {
        const data = await getUnits(type);
        setSafetyCenters(data);
      } catch {
        setSafetyCenters([]);
      } finally {
        setCentersLoading(false);
      }
    }
  }

  function handlePhone(e) {
    const digits = e.target.value.replace(/\D/g, '').slice(0, 11);
    let formatted = digits;
    if (digits.length > 7) formatted = `${digits.slice(0, 3)}-${digits.slice(3, 7)}-${digits.slice(7)}`;
    else if (digits.length > 3) formatted = `${digits.slice(0, 3)}-${digits.slice(3)}`;
    setForm((prev) => ({ ...prev, phone_number: formatted }));
  }

  function validate() {
    const e = {};
    if (!form.name.trim()) e.name = '이름을 입력하세요.';
    if (!form.email.trim()) e.email = '이메일을 입력하세요.';
    if (FACILITY_UNIT_TYPES.includes(form.unit_type) && !form.safety_center_id) {
      e.safety_center_id = `${form.unit_type}를 선택하세요.`;
    }
    if (form.unit_type === '본서' && !form.department) {
      e.department = '소속 과를 선택하세요.';
    }
    return e;
  }

  async function handleCreate() {
    const e = validate();
    if (Object.keys(e).length) { setErrors(e); return; }
    setLoading(true);
    try {
      const data = await createUser({
        name: form.name,
        email: form.email,
        phone_number: form.phone_number,
        rank: form.rank,
        unit_type: form.unit_type,
        safety_center_id: form.safety_center_id,
        department: form.department,
        station_id: user.station_id,
      });
      setResult(data);
    } catch (err) {
      setErrors({ general: err.response?.data?.detail || '계정 생성에 실패했습니다.' });
    } finally {
      setLoading(false);
    }
  }

  if (result) {
    return (
      <div className="admin-overlay" onClick={onClose}>
        <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
          <div className="admin-modal-header">
            <div className="admin-modal-title-row">
              <div className="admin-modal-icon-box admin-modal-icon-box--success">
                <i className="bi bi-person-check" />
              </div>
              <div>
                <div className="admin-modal-title">계정 생성 완료</div>
                <div className="admin-modal-subtitle">아래 정보를 대원에게 전달하세요</div>
              </div>
            </div>
            <button className="admin-modal-close" onClick={onClose}>
              <i className="bi bi-x-lg" />
            </button>
          </div>
          <div className="admin-modal-body">
            <div className="admin-warn-banner">
              <i className="bi bi-exclamation-triangle-fill" />
              이 화면을 닫으면 임시 비밀번호를 다시 확인할 수 없습니다.
            </div>
            <div className="admin-field">
              <label className="admin-field-label">대원번호 (로그인 아이디)</label>
              <input className="admin-input" value={result.firefighter_number} readOnly />
            </div>
            <div className="admin-field">
              <label className="admin-field-label">임시 비밀번호</label>
              <input className="admin-input" value={result.temp_password} readOnly />
            </div>
          </div>
          <div className="admin-modal-footer">
            <button className="admin-btn-confirm" onClick={() => { onCreated(); onClose(); }}>
              확인했습니다
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-overlay" onClick={onClose}>
      <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
        <div className="admin-modal-header">
          <div className="admin-modal-title-row">
            <div className="admin-modal-icon-box">
              <i className="bi bi-person-plus" />
            </div>
            <div>
              <div className="admin-modal-title">사용자 추가</div>
              <div className="admin-modal-subtitle">새 대원 계정을 직접 발급합니다</div>
            </div>
          </div>
          <button className="admin-modal-close" onClick={onClose}>
            <i className="bi bi-x-lg" />
          </button>
        </div>

        <div className="admin-modal-body">
          {errors.general && (
            <div className="admin-error-banner">{errors.general}</div>
          )}

          <div className="admin-modal-two-col">
            <div className="admin-field">
              <label className="admin-field-label">이름 <span className="admin-required">*</span></label>
              <input
                className={`admin-input${errors.name ? ' is-error' : ''}`}
                placeholder="대원 이름"
                value={form.name}
                onChange={set('name')}
              />
              {errors.name && <span className="admin-field-error">{errors.name}</span>}
            </div>
            <div className="admin-field">
              <label className="admin-field-label">계급</label>
              <div className="admin-chips">
                {RANKS.map((r) => (
                  <button
                    key={r}
                    type="button"
                    className={`admin-chip${form.rank === r ? ' active' : ''}`}
                    onClick={() => setForm((prev) => ({ ...prev, rank: r }))}
                  >
                    {r}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="admin-field">
            <label className="admin-field-label">이메일</label>
            <input
              className={`admin-input${errors.email ? ' is-error' : ''}`}
              placeholder="이메일"
              value={form.email}
              onChange={set('email')}
            />
            {errors.email && <span className="admin-field-error">{errors.email}</span>}
          </div>

          <div className="admin-field">
            <label className="admin-field-label">연락처</label>
            <input
              className="admin-input"
              placeholder="010-0000-0000"
              value={form.phone_number}
              onChange={handlePhone}
            />
            <span className="admin-field-hint">대원이 최초 로그인 후 직접 비밀번호를 변경하게 됩니다.</span>
          </div>

          <div className="admin-field">
            <label className="admin-field-label">소속 유형</label>
            <div className="admin-chips">
              {UNIT_TYPES.map((u) => (
                <button
                  key={u}
                  type="button"
                  className={`admin-chip${form.unit_type === u ? ' active' : ''}`}
                  onClick={() => handleUnitTypeChange(u)}
                >
                  {u}
                </button>
              ))}
            </div>
          </div>

          {FACILITY_UNIT_TYPES.includes(form.unit_type) && (
            <div className="admin-field">
              <label className="admin-field-label">{form.unit_type} 선택 <span className="admin-required">*</span></label>
              {centersLoading ? (
                <span className="admin-field-hint">불러오는 중…</span>
              ) : safetyCenters.length === 0 ? (
                <span className="admin-field-hint">등록된 {form.unit_type}가 없습니다.</span>
              ) : (
                <div className="admin-chips admin-chips--grid3">
                  {safetyCenters.map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      className={`admin-chip${form.safety_center_id === c.id ? ' active' : ''}`}
                      onClick={() => setForm((prev) => ({ ...prev, safety_center_id: c.id }))}
                    >
                      {c.name}
                    </button>
                  ))}
                </div>
              )}
              {errors.safety_center_id && (
                <span className="admin-field-error">{errors.safety_center_id}</span>
              )}
            </div>
          )}

          {form.unit_type === '본서' && (
            <div className="admin-field">
              <label className="admin-field-label">소속 과 <span className="admin-required">*</span></label>
              <div className="admin-chips admin-chips--grid3">
                {DEPARTMENTS.map((d) => (
                  <button
                    key={d}
                    type="button"
                    className={`admin-chip${form.department === d ? ' active' : ''}`}
                    onClick={() => setForm((prev) => ({ ...prev, department: d }))}
                  >
                    {d}
                  </button>
                ))}
              </div>
              {errors.department && (
                <span className="admin-field-error">{errors.department}</span>
              )}
            </div>
          )}
        </div>

        <div className="admin-modal-footer">
          <button className="admin-btn-cancel" onClick={onClose}>취소</button>
          <button className="admin-btn-confirm" onClick={handleCreate} disabled={loading}>
            {loading ? '생성 중…' : '계정 생성'}
          </button>
        </div>
      </div>
    </div>
  );
}

function EditModal({ member, onClose, onSaved }) {
  const [loadingReset, setLoadingReset] = useState(false);
  const [loadingSave, setLoadingSave] = useState(false);
  const [resetDone, setResetDone] = useState(false);
  const [newPassword, setNewPassword] = useState(null);

  const [safetyCenters, setSafetyCenters] = useState([]);
  const [centersLoading, setCentersLoading] = useState(false);
  const [selectedUnitType, setSelectedUnitType] = useState(member.unit_type ?? '본서');
  const [selectedCenterId, setSelectedCenterId] = useState(member.safety_center_id ?? null);
  const [selectedDepartment, setSelectedDepartment] = useState(member.department ?? null);
  const [transferStationId, setTransferStationId] = useState('');

  async function handleUnitTypeChange(type) {
    setSelectedUnitType(type);
    setSelectedCenterId(null);
    setSelectedDepartment(null);
    if (FACILITY_UNIT_TYPES.includes(type)) {
      setCentersLoading(true);
      setSafetyCenters([]);
      try {
        const data = await getUnits(type);
        setSafetyCenters(data);
      } catch {
        setSafetyCenters([]);
      } finally {
        setCentersLoading(false);
      }
    }
  }

  useEffect(() => {
    if (FACILITY_UNIT_TYPES.includes(member.unit_type)) {
      Promise.resolve().then(() => {
        setCentersLoading(true);
        getUnits(member.unit_type)
          .then(setSafetyCenters)
          .catch(() => setSafetyCenters([]))
          .finally(() => setCentersLoading(false));
      });
    }
  }, [member.unit_type]);

  async function handleReset() {
    setLoadingReset(true);
    try {
      const data = await resetUserPassword(member.firefighter_number);
      setResetDone(true);
      setNewPassword(data.temp_password);
    } catch {
      // 필요 시 에러 처리 추가
    } finally {
      setLoadingReset(false);
    }
  }

  async function handleSave() {
    setLoadingSave(true);
    try {
      const payload = {
        unit_type: selectedUnitType,
        safety_center_id: FACILITY_UNIT_TYPES.includes(selectedUnitType) ? selectedCenterId : null,
        department: selectedUnitType === '본서' ? selectedDepartment : null,
      };
      if (transferStationId.trim()) payload.station_id = Number(transferStationId);
      await client.patch(`/admin/users/${member.id}`, payload);
      onSaved();
    } catch {
      // 필요 시 에러 처리 추가
    } finally {
      setLoadingSave(false);
    }
  }

  return (
    <div className="admin-overlay" onClick={onClose}>
      <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
        <div className="admin-modal-header admin-modal-header--edit">
          <div className="admin-modal-title-row">
            <div className="admin-modal-avatar">{member.name[0]}</div>
            <div>
              <div className="admin-modal-title">{member.name} 대원 관리</div>
              <div className="admin-modal-subtitle">{member.firefighter_number}</div>
            </div>
          </div>
          <button className="admin-modal-close" onClick={onClose}>
            <i className="bi bi-x-lg" />
          </button>
        </div>

        <div className="admin-modal-body">
          <div className="admin-modal-section">
            <div className="admin-section-title">비밀번호 초기화</div>
            <button
              className={`admin-reset-btn${resetDone ? ' done' : ''}`}
              onClick={handleReset}
              disabled={loadingReset || resetDone}
            >
              <i className={`bi bi-${resetDone ? 'check-lg' : 'arrow-counterclockwise'}`} />
              {resetDone ? '초기화 완료' : loadingReset ? '처리 중…' : '비밀번호 초기화하기'}
            </button>
            {newPassword && (
              <div className="admin-field">
                <div className="admin-warn-banner">
                  <i className="bi bi-exclamation-triangle-fill" />
                  이 화면을 닫으면 임시 비밀번호를 다시 확인할 수 없습니다.
                </div>
                <label className="admin-field-label">새 임시 비밀번호</label>
                <input className="admin-input" value={newPassword} readOnly />
              </div>
            )}
          </div>

          <div className="admin-modal-section">
            <div className="admin-section-title">소속 센터 변경</div>
            <div className="admin-field-hint admin-field-hint--current">
              현재 소속 &nbsp;·&nbsp;
              <span>{member.station_name}</span>
              {member.unit_name && <> &nbsp;/&nbsp; <span>{member.unit_name}</span></>}
              {member.department && <> &nbsp;/&nbsp; <span>{member.department}</span></>}
            </div>
            <div className="admin-chips">
              {UNIT_TYPES.map((u) => (
                <button
                  key={u}
                  type="button"
                  className={`admin-chip${selectedUnitType === u ? ' active' : ''}`}
                  onClick={() => handleUnitTypeChange(u)}
                >
                  {u}
                </button>
              ))}
            </div>
            {FACILITY_UNIT_TYPES.includes(selectedUnitType) && (
              centersLoading ? (
                <span className="admin-field-hint">불러오는 중…</span>
              ) : safetyCenters.length === 0 ? (
                <span className="admin-field-hint">등록된 {selectedUnitType}가 없습니다.</span>
              ) : (
                <div className="admin-chips admin-chips--grid3">
                  {safetyCenters.map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      className={`admin-chip${selectedCenterId === c.id ? ' active' : ''}`}
                      onClick={() => setSelectedCenterId(c.id)}
                    >
                      {c.name}
                    </button>
                  ))}
                </div>
              )
            )}
            {selectedUnitType === '본서' && (
              <div className="admin-chips admin-chips--grid3">
                {DEPARTMENTS.map((d) => (
                  <button
                    key={d}
                    type="button"
                    className={`admin-chip${selectedDepartment === d ? ' active' : ''}`}
                    onClick={() => setSelectedDepartment(d)}
                  >
                    {d}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="admin-modal-section">
            <div className="admin-section-title">타지 소방서 이동</div>
            <div className="admin-field">
              <input
                className="admin-input"
                placeholder="이동할 소방서 ID 입력"
                value={transferStationId}
                onChange={(e) => setTransferStationId(e.target.value)}
              />
              <span className="admin-field-hint">입력 시 해당 소방서로 소속이 변경됩니다.</span>
            </div>
          </div>
        </div>

        <div className="admin-modal-footer">
          <button className="admin-btn-cancel" onClick={onClose}>취소</button>
          <button className="admin-btn-confirm" onClick={handleSave} disabled={loadingSave}>
            {loadingSave ? '저장 중…' : '변경 저장'}
          </button>
        </div>
      </div>
    </div>
  );
}

function Admin() {
  const user = useUser();
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [modal, setModal] = useState(null);

  const fetchMembers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getStationUsers();
      setMembers(data);
    } catch {
      setError('대원 목록을 불러오지 못했습니다.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    Promise.resolve().then(() => fetchMembers());
  }, [fetchMembers]);

  function handleCreated() {
    setModal(null);
    fetchMembers();
  }

  function handleSaved() {
    setModal(null);
    fetchMembers();
  }

  return (
    <div className="admin">
      <div className="admin-page-header">
        <div>
          <h1 className="admin-page-title">소속 대원 계정</h1>
          <p className="admin-page-subtitle">{user?.station_name}에 최종 소속된 현재 사용자 목록입니다</p>
        </div>
        <button className="admin-add-btn" onClick={() => setModal('add')}>
          <i className="bi bi-plus-lg" /> 사용자 추가
        </button>
      </div>

      <div className="admin-card">
        <table className="admin-table">
          <thead>
            <tr>
              <th>대원</th>
              <th>계급</th>
              <th>이메일</th>
              <th>소속 센터</th>
              <th>관리</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={5} className="admin-table-status">불러오는 중…</td>
              </tr>
            ) : error ? (
              <tr>
                <td colSpan={5} className="admin-table-status admin-table-status--error">{error}</td>
              </tr>
            ) : members.length === 0 ? (
              <tr>
                <td colSpan={5} className="admin-table-status">등록된 대원이 없습니다.</td>
              </tr>
            ) : members.map((m) => (
              <tr key={m.id}>
                <td>
                  <div className="admin-member">
                    <div className="admin-row-avatar">{m.name[0]}</div>
                    <div className="admin-member-info">
                      <span className="admin-member-name">{m.name}</span>
                    </div>
                  </div>
                </td>
                <td className="admin-cell">{m.rank}</td>
                <td className="admin-cell">{m.email}</td>
                <td className="admin-cell admin-cell--station">{m.unit_name}</td>
                <td className="admin-cell admin-cell--action">
                  <button
                    className="admin-edit-btn"
                    onClick={() => setModal({ type: 'edit', member: m })}
                  >
                    수정
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modal === 'add' && (
        <AddModal onClose={() => setModal(null)} onCreated={handleCreated} />
      )}
      {modal?.type === 'edit' && (
        <EditModal
          member={modal.member}
          onClose={() => setModal(null)}
          onSaved={handleSaved}
        />
      )}
    </div>
  );
}

function AdminPage() {
  return (
    <DashboardLayout>
      <Admin />
    </DashboardLayout>
  );
}

export default AdminPage;
