import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './apps/firefighter_dashboard/pages/login';
import FindPW from './apps/firefighter_dashboard/pages/findpw';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './shared/style/global.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<Login />} />
        <Route path='/findpw' element={<FindPW />}/>
      </Routes>
    </BrowserRouter>
  )
}

export default App
