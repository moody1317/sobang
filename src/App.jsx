import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './apps/firefighter_dashboard/pages/login';
import FindPW from './apps/firefighter_dashboard/pages/findpw';
import BriefingPage from './apps/firefighter_dashboard/pages/briefing';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './shared/style/global.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<Login />} />
        <Route path='/findpw' element={<FindPW />}/>
        <Route path='/dashboard' element={<BriefingPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
