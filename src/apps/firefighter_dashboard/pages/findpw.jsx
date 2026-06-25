import { Link } from 'react-router-dom';
import AuthLayout from "../layouts/authlayout";
import './findpw.css';

function FindPW() {
    return (
        <AuthLayout>
            <div className="findpw-container">
                <div className="findpw-header">
                    <div className="findpw-icon">
                        <i className="bi bi-lock"/>
                    </div>
                    <h2 className="findpw-title">비밀번호 찾기</h2>
                    <p className="findpw-subtitle">
                        본인 확인 절차가 필요한 보안 정보입니다.<br/>
                        소속 소방서 관리자에게 문의하시면 임시 비밀번호를 재발급받을 수 있습니다.
                    </p>
                </div>

                <div className="findpw-notice">
                    <i className="bi bi-info-circle" />
                    <p>관리자 문의: 소속 소방서 행정실 또는 시스템 담당자</p>
                </div>

                <Link to="/" className="login-link">로그인으로 돌아가기</Link>
            </div>
        </AuthLayout>
    )
}

export default FindPW;