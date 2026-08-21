import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Labs from './pages/Labs'
import LabDetails from './pages/LabDetails'
import ScanResults from './pages/ScanResults'
import Report from './pages/Report'
import Profile from './pages/Profile'
import Settings from './pages/Settings'
import Attacks from './pages/Attacks'
import ScanHistory from './pages/ScanHistory'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout /> }>
          <Route index element={<Home />} />
          <Route path="login" element={<Login />} />
          <Route path="register" element={<Register />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="labs" element={<Labs />} />
          <Route path="lab/:id" element={<LabDetails />} />
          <Route path="lab/:id/attacks" element={<Attacks />} />
          <Route path="scan/:id" element={<ScanResults />} />
          <Route path="report/:id" element={<Report />} />
          <Route path="profile" element={<Profile />} />
          <Route path="settings" element={<Settings />} />
          <Route path="scans/history" element={<ScanHistory />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App