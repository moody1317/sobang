import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { UserProvider } from './apps/firefighter_dashboard/contexts/usercontext';
import ProtectedRoute from './shared/components/ProtectedRoute';
import Login from './apps/firefighter_dashboard/pages/login';
import FindPW from './apps/firefighter_dashboard/pages/findpw';
import BriefingPage from './apps/firefighter_dashboard/pages/briefing';
import MyPagePage from './apps/firefighter_dashboard/pages/mypage';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './shared/style/global.css';

function App() {
  return (
    <UserProvider>
      <BrowserRouter>
        <Routes>
          <Route path='/' element={<Login />} />
          <Route path='/findpw' element={<FindPW />}/>
          <Route
            path='/dashboard'
            element={
              <ProtectedRoute>
                <BriefingPage />
              </ProtectedRoute>
            }
          />
          <Route
            path='/dashboard/profile'
            element={
              <ProtectedRoute>
                <MyPagePage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </UserProvider>
  )
}

export default App