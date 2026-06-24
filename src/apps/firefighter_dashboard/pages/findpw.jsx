import { useState } from "react";
import { Link } from 'react-router-dom';
import AuthLayout from "../layouts/authlayout";
import './findpw.css';

function FindPW() {
    function handleSubmit(e) {
        e.preventDefault();
    }

    return (
        <AuthLayout>
            <div className="findpw-container">
                <div className="findpw-header">
                    <div className="findpw-icon">
                        <i className="bi bi-lock"/>
                    </div>
                    <h2 className="findpw-title">비밀번호 찾기</h2>
                    <p className="findpw-subtitle">대원번호와 소방서 코드를 확인한 뒤, 등록된 이메일로 임시 비밀번호를 보내드립니다.</p>
                </div>
                
                <form className="findpw-form" onSubmit={handleSubmit}>
                    <div className="form-field">
                        <label className="form-label">대원번호</label>
                        <input
                            type="text"
                            className="form-input"
                            placeholder="cjsd0123"
                        />
                    </div>
                    <div className="form-field">
                        <label className="form-label">소방서 코드</label>
                        <input
                            type="text"
                            className="form-input"
                            placeholder="cjsd"
                        />
                    </div>
                    <button type="submit" className="findpw-btn">임시 비밀번호 보내기</button>
                </form>

                <Link to="/" className="login-link">로그인으로 돌아가기</Link>
            </div>
        </AuthLayout>
    )
}

export default FindPW;