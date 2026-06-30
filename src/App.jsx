import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { UserProvider } from './apps/firefighter_dashboard/contexts/usercontext';
import { AlertProvider } from './apps/firefighter_dashboard/contexts/alertcontext';
import ProtectedRoute from './shared/components/ProtectedRoute';
import Login from './apps/firefighter_dashboard/pages/login';
import FindPW from './apps/firefighter_dashboard/pages/findpw';
import BriefingPage from './apps/firefighter_dashboard/pages/briefing';
import MyPagePage from './apps/firefighter_dashboard/pages/mypage';
import AdminPage from './apps/firefighter_dashboard/pages/admin';
import ChangePassword from './apps/firefighter_dashboard/pages/changepw';
import DataPagePage from './apps/firefighter_dashboard/pages/data';
import DangerPage from './apps/firefighter_dashboard/pages/danger';
import Alert from './apps/firefighter_dashboard/pages/alert';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './shared/style/global.css';

function App() {
  return (
    <AlertProvider>
    <UserProvider>
      <BrowserRouter>
        <Routes>
          <Route path='/' element={<Login />} />
          <Route path='/findpw' element={<FindPW />}/>
          <Route
            path='/change-password'
            element={
              <ProtectedRoute>
                <ChangePassword />
              </ProtectedRoute>
            }
          />
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
          <Route
            path='/dashboard/admin'
            element={
              <ProtectedRoute>
                <AdminPage />
              </ProtectedRoute>
            }
          />
          <Route
            path='/dashboard/data'
            element={
              <ProtectedRoute>
                <DataPagePage />
              </ProtectedRoute>
            }
          />
          <Route
            path='/dashboard/map'
            element={
              <ProtectedRoute>
                <DangerPage />
              </ProtectedRoute>
            }
          />
          <Route
            path='/dashboard/alerts'
            element={
              <ProtectedRoute>
                <Alert/>
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </UserProvider>
    </AlertProvider>
  )
}

export default App