import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { AppShell } from '@/components/AppShell'
import DashboardPage from '@/pages/DashboardPage'
import KnowledgePage from '@/pages/KnowledgePage'
import OperationsPage from '@/pages/OperationsPage'
import { useOpsStore } from '@/store/useOpsStore'

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/knowledge" element={<KnowledgePage />} />
      <Route path="/operations" element={<OperationsPage />} />
    </Routes>
  )
}

export default function App() {
  const connection = useOpsStore((state) => state.connection)
  const generatedAt = useOpsStore((state) => state.snapshot?.generatedAt)

  return (
    <BrowserRouter>
      <AppShell connection={connection} generatedAt={generatedAt}>
        <AppRoutes />
      </AppShell>
    </BrowserRouter>
  )
}
