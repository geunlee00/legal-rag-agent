import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Landing from './pages/Landing'
import Diagnose from './pages/Diagnose'

// 주소(URL) → 페이지 연결.
// Layout이 공통 뼈대(헤더·푸터)를 감싸고, 그 안에 각 페이지가 들어간다.
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Landing />} />
        <Route path="/diagnose" element={<Diagnose />} />
      </Route>
    </Routes>
  )
}
